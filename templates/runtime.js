(() => {
  const data=JSON.parse(document.getElementById('runtime-data').textContent);
  const spec=data.spec, own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
  const el=id=>document.getElementById(id);
  const create=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const fail=m=>{throw new Error(m);};
  const clone=v=>JSON.parse(JSON.stringify(v));
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const format=n=>finite(n)?Number(n.toPrecision(7)).toString():String(n);
  const tickNumber=n=>finite(n)?Number(n.toPrecision(3)).toString():String(n);
  const unit=u=>u||'units not specified';
  const shortLabel=label=>label.length>10?label.slice(0,9)+'…':label;
  const leavesOf=v=>Array.isArray(v)?v.reduce((xs,x)=>xs.concat(leavesOf(x)),[]):[v];
  function shape(v,depth=0) {
    if(finite(v))return {dims:[],leaves:1};
    if(!Array.isArray(v)||v.length<1||v.length>8||depth>=8)fail('Numeric values must be finite and dimensions must be 1–8');
    const children=v.map(x=>shape(x,depth+1)),dims=children[0].dims;
    if(children.some(x=>JSON.stringify(x.dims)!==JSON.stringify(dims)))fail('Numeric arrays must be rectangular');
    const leaves=children.reduce((s,x)=>s+x.leaves,0);if(leaves>128)fail('Numeric leaf limit is 128');
    return {dims:[v.length,...dims],leaves};
  }
  function validate(values,clamp=false) {
    const keys=spec.controls.map(c=>c.id);if(Object.keys(values).length!==keys.length||Object.keys(values).some(k=>!keys.includes(k)))fail('Unknown or missing control');
    const result=Object.create(null);let leaves=0;
    for(const c of spec.controls) {
      let value=values[c.id];
      if(c.kind==='toggle'){if(typeof value!=='boolean')fail(c.label+': expected a boolean');}
      else if(c.kind==='select'){if(typeof value!=='string'||!c.options.some(o=>o.value===value))fail(c.label+': unavailable option');}
      else {
        const s=shape(value);if(JSON.stringify(s.dims)!==JSON.stringify(c.shape||[]))fail(c.label+': wrong shape');leaves+=s.leaves;
        const bounded=v=>{if(Array.isArray(v))return v.map(bounded);if(clamp)return Math.min(c.max,Math.max(c.min,v));if(v<c.min||v>c.max)fail(c.label+': out of bounds');return v;};value=bounded(value);
      }
      result[c.id]=clone(value);
    }
    if(leaves>128)fail('Total input numeric leaf limit is 128');return result;
  }
  function merge(patch) {
    if(!patch||Array.isArray(patch)||typeof patch!=='object')fail('Preset must be an input dictionary');
    const defaults=Object.create(null);for(const c of spec.controls)defaults[c.id]=clone(c.default);
    for(const key of Object.keys(patch)){if(!own(defaults,key))fail('Unknown preset control');defaults[key]=clone(patch[key]);}
    return validate(defaults);
  }
  function outputs(value) {
    if(!value||typeof value!=='object'||Array.isArray(value))fail('Compute must return an output dictionary');
    const keys=spec.outputs.map(o=>o.id);if(Object.keys(value).length!==keys.length||Object.keys(value).some(k=>!keys.includes(k)))fail('Compute returned missing or extra output keys');
    let leaves=0;for(const o of spec.outputs){if(!own(value,o.id))fail('Missing output: '+o.id);leaves+=shape(value[o.id]).leaves;}
    if(leaves>128)fail('Total output numeric leaf limit is 128');return value;
  }
  const compute=(inputs,b)=>outputs(NumericRuntime.run(data.ast,inputs,b));
  let state,last=null;const widgets=new Map();
  function status(message,error=false){el('status').textContent=message;el('status').className=error?'error':'';}
  function sync(){for(const c of spec.controls){const ws=widgets.get(c.id);if(!ws)continue;const value=state[c.id];for(const w of ws){const v=w.path.reduce((x,i)=>x[i],value);if(c.kind==='toggle')w.node.checked=v;else w.node.value=String(v);w.node.removeAttribute('aria-invalid');}const read=el('read-'+c.id);if(read)read.textContent=format(value)+' '+c.units;}}
  function edit(c,w) {
    try {
      let value;if(c.kind==='toggle')value=w.node.checked;else if(c.kind==='select')value=w.node.value;
      else {if(w.node.value.trim()===''||w.node.validity.badInput)fail(c.label+': enter a finite number');value=Number(w.node.value);if(!finite(value))fail(c.label+': enter a finite number');}
      const proposed=clone(state);if(!w.path.length)proposed[c.id]=value;else{let target=proposed[c.id];for(const i of w.path.slice(0,-1))target=target[i];target[w.path[w.path.length-1]]=value;}
      state=validate(proposed,true);sync();recalculate();
    }catch(error){sync();w.node.setAttribute('aria-invalid','true');status('Invalid edit; last valid inputs retained. '+error.message,true);}
  }
  function controls() {
    for(const c of spec.controls) {
      const field=create('fieldset',undefined,el('controls'));create('legend',c.label+' ('+unit(c.units)+')',field);
      const help=create('small',c.help,field);help.id='help-'+c.id;const ws=[];widgets.set(c.id,ws);
      const add=(path,type,parent,label)=>{
        const box=create('div',undefined,parent),id='input-'+c.id+'-'+(path.join('-')||'scalar');
        const lab=create('label',label,box);lab.htmlFor=id;
        const node=create(type==='select'?'select':'input',undefined,box);node.id=id;node.setAttribute('aria-describedby',help.id);
        if(type==='select')for(const o of c.options){const option=create('option',o.label,node);option.value=o.value;}
        else{node.type=type;if(type==='number'||type==='range'){node.min=String(c.min);node.max=String(c.max);node.step=String(c.step);}}
        const w={node,path};ws.push(w);node.addEventListener(type==='range'?'input':'change',()=>edit(c,w));return node;
      };
      if(c.kind==='vector'||c.kind==='matrix') {
        const scroll=create('div',undefined,field);scroll.className='scroll';const grid=create('div',undefined,scroll);grid.className='grid';
        if(c.kind==='matrix'){grid.style.gridTemplateColumns='repeat('+c.shape[1]+', minmax(110px,1fr))';grid.style.minWidth=(110*c.shape[1])+'px';}
        for(let row=0;row<c.shape[0];row++)for(let col=0;col<(c.kind==='matrix'?c.shape[1]:1);col++){
          const path=c.kind==='matrix'?[row,col]:[row];add(path,'number',grid,c.kind==='matrix'?'Row '+(row+1)+', column '+(col+1):'Element '+(row+1));}
      }else{add([],c.kind==='toggle'?'checkbox':c.kind==='select'?'select':c.kind==='slider'?'range':'number',field,c.label);if(c.kind==='slider'){const read=create('output','',field);read.id='read-'+c.id;read.htmlFor=ws[0].node.id;}}
    }
  }
  function renderOutputs(result) {
    el('outputs').replaceChildren();
    for(const o of spec.outputs){const box=create('div',undefined,el('outputs'));box.className='output';create('h3',o.label+' — '+o.role+' ('+unit(o.units)+')',box);const value=result[o.id];create('pre',Array.isArray(value)?JSON.stringify(value,null,2):format(value),box);}
  }
  const ns='http://www.w3.org/2000/svg';
  function svgNode(tag,attrs,parent,text){const n=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;}
  function chart(v,parent){const svg=svgNode('svg',{viewBox:'0 0 640 360',role:'img','aria-label':v.title},parent);svgNode('title',{},svg,v.title);return svg;}
  function axis(svg,v,xmin,xmax,ymin,ymax,xUnits,yUnits,categories=false) {
    svgNode('path',{d:'M 88 30 V 284 H 608',fill:'none',stroke:'#425e70'},svg);
    for(let i=0;i<=4;i++){const y=284-i*60;svgNode('line',{x1:88,x2:608,y1:y,y2:y,stroke:'#dae3e9'},svg);svgNode('text',{x:80,y:y+4,'text-anchor':'end'},svg,tickNumber(ymin+(ymax-ymin)*i/4));}
    if(!categories)for(let i=0;i<=4;i++)svgNode('text',{x:88+i*130,y:306,'text-anchor':'middle'},svg,tickNumber(xmin+(xmax-xmin)*i/4));
    svgNode('text',{x:348,y:340,'text-anchor':'middle'},svg,v.x_label+(xUnits?' ('+xUnits+')':''));
    svgNode('text',{transform:'translate(18 160) rotate(-90)','text-anchor':'middle'},svg,v.y_label+' ('+unit(yUnits)+')');
  }
  function domain(values,zero=false){let min=Math.min(...values),max=Math.max(...values);if(zero){min=Math.min(0,min);max=Math.max(0,max);}if(min===max){const d=Math.max(1,Math.abs(min)*.1);min-=d;max+=d;}if(!finite(max-min))fail('Chart numeric range is too large');return [min,max];}
  function numericTable(value,title,parent,labels) {
    const div=create('div',undefined,parent);div.className='scroll';const table=create('table',undefined,div);create('caption',title,table);
    const rows=Array.isArray(value)?(Array.isArray(value[0])?value:value.map(x=>[x])):[[value]];
    if(rows.some(r=>r.some(Array.isArray))){create('pre',JSON.stringify(value,null,2),parent);return;}
    const head=create('tr',undefined,create('thead',undefined,table));create('th','Index',head);
    for(let i=0;i<rows[0].length;i++){const th=create('th','Column '+(i+1),head);th.scope='col';}
    const body=create('tbody',undefined,table);rows.forEach((r,i)=>{const tr=create('tr',undefined,body);const th=create('th',(labels&&labels[i])||'Row '+(i+1),tr);th.scope='row';r.forEach(x=>create('td',format(x),tr));});
  }
  function renderVisual(v,result,inputs,b,parent) {
    const output=spec.outputs.find(o=>o.id===v.output),value=result[v.output],s=shape(value);
    create('h3',v.title,parent);
    if(v.kind==='values'){numericTable(value,output.label+' ('+unit(output.units)+')',parent,v.labels);return;}
    if(v.kind==='heatmap') {
      if(s.dims.length!==2)fail('Heatmap requires a matrix');
      create('p',v.x_label+' × '+v.y_label+'; '+output.label+(output.units?' ('+output.units+')':''),parent);
      const svg=chart(v,parent),flat=leavesOf(value),[lo,hi]=domain(flat),rows=value.length,cols=value[0].length;
      for(let r=0;r<rows;r++){const label=(v.labels&&v.labels[r])||String(r+1);const tick=svgNode('text',{x:80,y:55+r*220/rows,'text-anchor':'end'},svg,shortLabel(label));svgNode('title',{},tick,label);for(let c=0;c<cols;c++){
        const t=(value[r][c]-lo)/(hi-lo),x=90+c*510/cols,y=32+r*220/rows;
        const cell=svgNode('rect',{x,y,width:510/cols-2,height:220/rows-2,fill:'hsl(195 45% '+(94-t*36)+'%)'},svg);svgNode('title',{},cell,'Row '+(r+1)+', column '+(c+1)+': '+format(value[r][c])+' '+unit(output.units));
        if(cols<=4)svgNode('text',{x:x+255/cols,y:y+110/rows+5,'text-anchor':'middle'},svg,tickNumber(value[r][c]));}}
      for(let c=0;c<cols;c++){const label=(v.labels&&v.labels[c])||String(c+1);const tick=svgNode('text',{x:90+(c+.5)*510/cols,y:276,'text-anchor':'middle'},svg,shortLabel(label));svgNode('title',{},tick,label);}
      svgNode('text',{x:350,y:310,'text-anchor':'middle'},svg,v.x_label);svgNode('text',{x:350,y:340,'text-anchor':'middle'},svg,'Scale: '+format(lo)+' to '+format(hi)+' '+unit(output.units));
      svgNode('text',{transform:'translate(18 150) rotate(-90)','text-anchor':'middle'},svg,v.y_label);numericTable(value,output.label+' ('+unit(output.units)+')',parent,v.labels);return;
    }
    if(v.kind==='bar') {
      if(s.dims.length!==1)fail('Bar chart requires a vector');
      const svg=chart(v,parent),[lo,hi]=domain(value,true);axis(svg,v,1,value.length,lo,hi,'',output.units,true);
      const y=x=>284-(x-lo)/(hi-lo)*240,zero=y(0),width=510/value.length;
      value.forEach((x,i)=>{svgNode('rect',{x:92+i*width,y:Math.min(zero,y(x)),width:Math.max(1,width-8),height:Math.abs(y(x)-zero),fill:'#207a96'},svg);svgNode('text',{x:92+(i+.5)*width,y:Math.max(38,Math.min(280,y(x)+(x<0?18:-7))),'text-anchor':'middle'},svg,format(x));const label=(v.labels&&v.labels[i])||String(i+1);const tick=svgNode('text',{x:92+(i+.5)*width,y:306,'text-anchor':'middle'},svg,label.length>10?label.slice(0,9)+'…':label);svgNode('title',{},tick,label);});
      numericTable(value,output.label+' ('+unit(output.units)+')',parent,v.labels);return;
    }
    if(v.kind==='line') {
      if(s.dims.length!==0)fail('Line chart requires a scalar output');
      const sw=v.sweep,control=spec.controls.find(c=>c.id===sw.control),points=[];
      for(let i=0;i<sw.points;i++){const x=i===sw.points-1?sw.max:sw.min+(sw.max-sw.min)*i/(sw.points-1),next=clone(inputs);next[sw.control]=x;const value=compute(validate(next),b)[v.output];if(!finite(value))fail('Sweep output must be scalar');points.push([x,value]);}
      const svg=chart(v,parent),[lo,hi]=domain(points.map(p=>p[1]));axis(svg,v,sw.min,sw.max,lo,hi,control.units,output.units);
      svgNode('polyline',{points:points.map(([x,y])=>(88+(x-sw.min)/(sw.max-sw.min)*520)+','+(284-(y-lo)/(hi-lo)*240)).join(' '),fill:'none',stroke:'#207a96','stroke-width':3},svg);
      numericTable(points,'Sweep: '+v.x_label+' ('+control.units+'), '+output.label+' ('+output.units+')',parent);return;
    }
    fail('Unsupported visual');
  }
  function compare(a,e,t) {
    if(Array.isArray(e))return Array.isArray(a)&&a.length===e.length&&e.every((v,i)=>compare(a[i],v,t));
    return finite(a)&&finite(e)&&Math.abs(a-e)<=t.atol+t.rtol*Math.abs(e);
  }
  function invariant(t,result) {
    const value=result[t.output],s=shape(value),leaves=leavesOf(value);
    if(t.kind==='finite')return leaves.every(finite);
    if(t.kind==='range')return leaves.every(x=>x>=t.min-(t.atol+t.rtol*Math.abs(t.min))&&x<=t.max+(t.atol+t.rtol*Math.abs(t.max)));
    if(t.kind==='sum'){if(s.dims.length!==1)fail('Sum invariant requires vector');return compare(value.reduce((a,c)=>a+c,0),t.expected,t);}
    if(t.kind==='row_sum'){if(s.dims.length!==2)fail('Row sum invariant requires matrix');return value.every(row=>compare(row.reduce((a,c)=>a+c,0),t.expected,t));}
    if(t.kind==='nondecreasing'){if(s.dims.length!==1)fail('Nondecreasing invariant requires vector');return value.every((x,i)=>i===0||x+t.atol+t.rtol*Math.abs(value[i-1])>=value[i-1]);}
    fail('Unknown invariant');
  }
  function selfChecks(result,b) {
    const list=el('checks');list.replaceChildren();let passed=0,failed=0,skipped=0;
    const check=(name,fn)=>{let kind,detail;try{const result=fn(),ok=typeof result==='boolean'?result:result.ok;kind=ok?'pass':'fail';detail=ok?'pass':'fail: expectation not met';if(typeof result==='object')detail+='; '+result.detail;if(ok)passed++;else failed++;}catch(error){kind='fail';detail='fail: '+error.message;failed++;}const li=create('li',name+' — '+detail,list);li.className=kind;};
    for(const t of spec.tests)check(t.name,()=>{const actual=compute(merge(t.inputs),b),measured=Object.create(null);for(const key of Object.keys(t.expected))measured[key]=actual[key];return {ok:Object.keys(t.expected).every(k=>compare(actual[k],t.expected[k],t)),detail:'Measured '+JSON.stringify(measured)+'; expected '+JSON.stringify(t.expected)+'; atol '+t.atol+', rtol '+t.rtol};});
    const cases=[['Current',result]];
    for(const e of spec.explorations){try{cases.push([e.title,compute(merge(e.preset),b)]);}catch(error){check(e.title+' preset',()=>{throw error;});}}
    for(const [name,actual] of cases)for(const t of spec.invariants)check(name+': '+t.name,()=>{const value=actual[t.output];let measured=value,expected=t.kind;if(t.kind==='sum'){measured=value.reduce((a,c)=>a+c,0);expected=t.expected;}if(t.kind==='row_sum'){if(shape(value).dims.length!==2)fail('Row sum invariant requires matrix');measured=value.map(row=>row.reduce((a,c)=>a+c,0));expected='each row '+t.expected;}if(t.kind==='range')expected='['+t.min+', '+t.max+']';const output=spec.outputs.find(o=>o.id===t.output);return {ok:invariant(t,actual),detail:'Measured '+JSON.stringify(measured)+' ('+unit(output.units)+'); expected '+expected+'; atol '+t.atol+', rtol '+t.rtol};});
    el('check-status').textContent=passed+' passed; '+failed+' failed; '+skipped+' skipped.';
    el('check-status').className=failed?'fail':'pass';
  }
  function recalculate() {
    const b=NumericRuntime.budget(2000000);let result;
    try{result=compute(state,NumericRuntime.budget());last=result;renderOutputs(result);el('result-status').textContent='Current valid result.';}
    catch(error){status('Calculation failed. '+error.message,true);el('result-status').textContent=last?'Last valid result retained — stale for current inputs.':'No valid result available.';el('check-status').textContent='Degraded: current calculation failed; checks not run.';el('check-status').className='skip';el('checks').replaceChildren();return;}
    el('visuals').replaceChildren();let visualFailures=0;
    for(const v of spec.visuals){const box=create('div',undefined,el('visuals'));box.className='chart';try{renderVisual(v,result,state,b,box);}catch(error){visualFailures++;box.replaceChildren();create('h3',v.title,box);create('p','Visual unavailable: '+error.message,box).className='error';}}
    status(visualFailures?'Calculation valid; '+visualFailures+' visual(s) unavailable.':'Inputs and calculation valid.',visualFailures>0);
    try{selfChecks(result,b);}catch(error){el('check-status').textContent='Degraded: '+error.message;el('check-status').className='skip';}
  }
  if(data.error||!data.ast){status('Degraded: '+(data.error||'Compute unavailable'),true);el('check-status').textContent='Skipped: compute was not admitted.';document.querySelectorAll('.preset').forEach(button=>button.disabled=true);return;}
  try {
    state=merge({});controls();sync();
    document.querySelectorAll('.preset').forEach(button=>button.addEventListener('click',()=>{try{const next=merge(spec.explorations[Number(button.dataset.preset)].preset);state=next;sync();recalculate();}catch(error){status('Invalid preset; last valid inputs retained. '+error.message,true);}}));
    recalculate();
  }catch(error){status('Degraded: '+error.message,true);el('check-status').textContent='Skipped: initialization failed.';}
})();
