(() => {
  const data=JSON.parse(document.getElementById('runtime-data').textContent);
  const spec=data.spec, own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
  const el=id=>document.getElementById(id);
  const create=(tag,text,parent)=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n;};
  const fail=m=>{throw new Error(m);};
  const clone=v=>JSON.parse(JSON.stringify(v));
  const finite=v=>typeof v==='number'&&Number.isFinite(v);
  const format=n=>finite(n)?Number(n.toPrecision(7)).toString():String(n);
  const displayValue=v=>Array.isArray(v)?'['+v.map(displayValue).join(', ')+']':format(v);
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
  let state,last=null,previous=null,lastInputs=null;const widgets=new Map();
  // Display tolerance only: scientific calculations/check tolerances are unchanged.
  const changed=(current,before)=>finite(before)&&Math.abs(current-before)>1e-9+1e-7*Math.abs(before);
  function scalarReadout(value,before,units,parent){
    const current=create('p',format(value),parent);current.className='output-value';
    create('span',' '+unit(units)+' · Current',current).className='units';
    create('p',finite(before)?'Previous: '+String(before)+' '+unit(units)+(changed(value,before)?' · Changed':' · No meaningful change'):'Previous: none — initial calculation',parent).className='previous-value';
  }
  function status(message,error=false){el('status').textContent=message;el('status').className=error?'error':'';}
  function sync(){for(const c of spec.controls){const ws=widgets.get(c.id);if(!ws)continue;const value=state[c.id];for(const w of ws){const v=w.path.reduce((x,i)=>x[i],value);if(c.kind==='toggle')w.node.checked=v;else w.node.value=String(v);w.node.removeAttribute('aria-invalid');}const read=el('read-'+c.id);if(read)read.textContent=format(value)+' '+c.units;const error=el('error-'+c.id);if(error)error.textContent='';}}
  function edit(c,w) {
    try {
      let value;if(c.kind==='toggle')value=w.node.checked;else if(c.kind==='select')value=w.node.value;
      else {if(w.node.value.trim()===''||w.node.validity.badInput)fail(c.label+': enter a finite number');value=Number(w.node.value);if(!finite(value))fail(c.label+': enter a finite number');}
      const proposed=clone(state);if(!w.path.length)proposed[c.id]=value;else{let target=proposed[c.id];for(const i of w.path.slice(0,-1))target=target[i];target[w.path[w.path.length-1]]=value;}
      state=validate(proposed,true);sync();recalculate();
    }catch(error){sync();w.node.setAttribute('aria-invalid','true');el('error-'+c.id).textContent='Invalid edit; previous value restored. '+error.message;status('Invalid edit; last valid inputs retained. '+error.message,true);}
  }
  function controls() {
    for(const c of spec.controls) {
      const field=create('fieldset',undefined,el('controls'));create('legend',c.label+(c.units?' ('+c.units+')':''),field);
      const help=create('small',c.help,field);help.id='help-'+c.id;const ws=[];widgets.set(c.id,ws);
      const add=(path,type,parent,label)=>{
        const box=create('div',undefined,parent),id='input-'+c.id+'-'+(path.join('-')||'scalar');
        box.className=path.length?'cell':type==='checkbox'?'toggle-control':'scalar-control';
        const lab=create('label',label,box);lab.htmlFor=id;
        if(!path.length&&type!=='checkbox')lab.className='sr-only';
        const node=create(type==='select'?'select':'input',undefined,box);node.id=id;node.setAttribute('aria-describedby',help.id+' error-'+c.id);
        if(type==='select')for(const o of c.options){const option=create('option',o.label,node);option.value=o.value;}
        else{node.type=type;if(type==='number'||type==='range'){node.min=String(c.min);node.max=String(c.max);node.step=String(c.step);}}
        const w={node,path};ws.push(w);node.addEventListener(type==='range'?'input':'change',()=>edit(c,w));return node;
      };
      if(c.kind==='vector'||c.kind==='matrix') {
        const scroll=create('div',undefined,field);scroll.className='scroll';const grid=create('div',undefined,scroll);grid.className='grid';
        if(c.kind==='matrix'){grid.style.gridTemplateColumns='repeat('+c.shape[1]+', minmax(110px,1fr))';grid.style.minWidth=(110*c.shape[1])+'px';}
        for(let row=0;row<c.shape[0];row++)for(let col=0;col<(c.kind==='matrix'?c.shape[1]:1);col++){
          const path=c.kind==='matrix'?[row,col]:[row];add(path,'number',grid,c.kind==='matrix'?'Row '+(row+1)+', column '+(col+1):'Element '+(row+1));}
      }else{
        let read;
        if(c.kind==='slider'){const heading=create('div',undefined,field);heading.className='control-heading';create('span','Current value',heading);read=create('output','',heading);read.id='read-'+c.id;}
        add([],c.kind==='toggle'?'checkbox':c.kind==='select'?'select':c.kind==='slider'?'range':'number',field,c.label);
        if(read)read.htmlFor=ws[0].node.id;
      }
      const error=create('small','',field);error.id='error-'+c.id;error.className='field-error';
    }
  }
  function renderOutputs(result) {
    el('outputs').replaceChildren();
    const containers=new Map();
    let step=0;
    for(const o of spec.outputs){
      const box=create('div',undefined,el('outputs'));box.className='output';box.id='output-'+o.id;box.setAttribute('data-role',o.role);containers.set(o.id,box);
      create('h4',o.label+' — '+o.role+' ('+unit(o.units)+')',box);
      create('p',o.role==='result'?'Final result':'Step '+(++step)+' · Intermediate',box).className='readout-label';
      if(!Array.isArray(result[o.id]))scalarReadout(result[o.id],previous&&previous[o.id],o.units,box);
      else {
        const visual=spec.visuals.find(v=>v.output===o.id);
        numericTable(result[o.id],o.label+' · Current ('+unit(o.units)+')',box,visual&&visual.labels,{x:visual&&visual.x_label,y:visual&&visual.y_label,value:o.label+' ('+unit(o.units)+')'},previous&&previous[o.id],o.units);
      }
    }
    return containers;
  }
  function resultReadout(result,parent,snapshot=false) {
    parent.replaceChildren();parent.className=snapshot?'preset-result':'result-preview';
    if(snapshot)create('p','Result when this preset was applied',parent).className='readout-label';
    for(const o of spec.outputs.filter(o=>o.role==='result')){
      const link=create('a',o.label,parent);link.href='#output-'+o.id;
      if(Array.isArray(result[o.id])){
        const visual=spec.visuals.find(v=>v.output===o.id);
        numericTable(result[o.id],o.units||'Numeric values',parent,visual&&visual.labels,{x:visual&&visual.x_label,y:visual&&visual.y_label},snapshot?null:previous&&previous[o.id],o.units);
      }else if(snapshot){const value=create('p',format(result[o.id])+' '+unit(o.units),parent);value.className='output-value';}
      else scalarReadout(result[o.id],previous&&previous[o.id],o.units,parent);
    }
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
  function heatmapScale(output,values) {
    if(spec.invariants.some(t=>t.output===output&&t.kind==='range'&&t.min===0&&t.max===1))
      return {domain:[0,1],fixed:true,diverging:false};
    const min=Math.min(...values),max=Math.max(...values);
    if(min<0&&max>0){const extent=Math.max(Math.abs(min),Math.abs(max));if(!finite(2*extent))fail('Chart numeric range is too large');return {domain:[-extent,extent],fixed:false,diverging:true};}
    // Include zero for constant one-sided data without suggesting the other sign.
    return {domain:min===max?(min<0?[min,0]:[0,max||1]):domain(values),fixed:false,diverging:false};
  }
  function heatmapColor(t,diverging) {
    const neutral=[245,246,246],end=diverging&&t<.5?[185,140,105]:[110,157,166];
    const strength=diverging?Math.abs(2*t-1):t;
    return 'rgb('+neutral.map((n,i)=>Math.round(n+(end[i]-n)*strength)).join(',')+')';
  }
  function numericTable(value,title,parent,labels,axes={},before=null,units='') {
    if(before!==null&&before!==undefined&&JSON.stringify(shape(value).dims)!==JSON.stringify(shape(before).dims)){
      const prior=create('details',undefined,parent);create('summary','Shape changed · inspect previous values ('+unit(units)+')',prior);create('pre',displayValue(before),prior);
    }
    const div=create('div',undefined,parent);div.className='scroll';div.tabIndex=0;div.setAttribute('role','region');div.setAttribute('aria-label',title);const table=create('table',undefined,div);create('caption',title,table);
    const rows=Array.isArray(value)?(Array.isArray(value[0])?value:value.map(x=>[x])):[[value]];
    if(rows.some(r=>r.some(Array.isArray))){create('pre',displayValue(value),parent);return;}
    const matrix=Array.isArray(value)&&Array.isArray(value[0]);
    const rowAxis=axes.columns?'Sample':matrix?(axes.y||'Row'):(axes.x||'Index');
    const head=create('tr',undefined,create('thead',undefined,table));create('th',rowAxis,head).scope='col';
    for(let i=0;i<rows[0].length;i++){const label=axes.columns?axes.columns[i]:matrix?(axes.x||'Column')+' '+((labels&&labels[i])||(i+1)):(axes.value||'Value');const th=create('th',label,head);th.scope='col';}
    const priorRows=Array.isArray(before)?(Array.isArray(before[0])?before:before.map(x=>[x])):[[before]];
    const body=create('tbody',undefined,table);rows.forEach((r,i)=>{const tr=create('tr',undefined,body);const th=create('th',(labels&&labels[i])||rowAxis+' '+(i+1),tr);th.scope='row';r.forEach((x,j)=>{const old=priorRows[i]&&priorRows[i][j],different=before!==null&&before!==undefined&&(!finite(old)||changed(x,old));const cell=create('td',String(x),tr);cell.className='numeric-value'+(different?' changed-cell':'');if(different){cell.setAttribute('data-changed','true');create('span',finite(old)?'Changed · previous: '+String(old)+' '+unit(units):'Added · previous: not present',cell).className='cell-previous';}});});
  }
  function renderVisual(v,result,inputs,b,parent) {
    const output=spec.outputs.find(o=>o.id===v.output),value=result[v.output],s=shape(value);
    const tableAxes={x:v.x_label,y:v.y_label,value:output.label+' ('+unit(output.units)+')'};
    create('h5',v.title,parent);
    if(v.kind==='values'){numericTable(value,output.label+' ('+unit(output.units)+')',parent,v.labels,tableAxes);return;}
    create('small','Scroll horizontally to see the full plot.',parent).className='plot-hint';
    if(v.kind==='heatmap') {
      if(s.dims.length!==2)fail('Heatmap requires a matrix');
      create('p',v.x_label+' × '+v.y_label+'; '+output.label+(output.units?' ('+output.units+')':''),parent);
      const svg=chart(v,parent),flat=leavesOf(value),scale=heatmapScale(v.output,flat),[lo,hi]=scale.domain,rows=value.length,cols=value[0].length;
      for(let r=0;r<rows;r++){const label=(v.labels&&v.labels[r])||String(r+1);const tick=svgNode('text',{x:80,y:55+r*220/rows,'text-anchor':'end'},svg,shortLabel(label));svgNode('title',{},tick,label);for(let c=0;c<cols;c++){
        const t=Math.max(0,Math.min(1,(value[r][c]-lo)/(hi-lo))),x=90+c*510/cols,y=32+r*220/rows;
        const old=previous&&previous[v.output]&&previous[v.output][r]&&previous[v.output][r][c],different=previous&&(!finite(old)||changed(value[r][c],old));
        const cell=svgNode('rect',{x,y,width:510/cols-2,height:220/rows-2,fill:heatmapColor(t,scale.diverging),stroke:different?'#785514':'none','stroke-width':different?3:0},svg);svgNode('title',{},cell,'Row '+(r+1)+', column '+(c+1)+': '+format(value[r][c])+' '+unit(output.units));
        if(cols<=4)svgNode('text',{x:x+255/cols,y:y+110/rows+5,'text-anchor':'middle'},svg,tickNumber(value[r][c]));}}
      for(let c=0;c<cols;c++){const label=(v.labels&&v.labels[c])||String(c+1);const tick=svgNode('text',{x:90+(c+.5)*510/cols,y:276,'text-anchor':'middle'},svg,shortLabel(label));svgNode('title',{},tick,label);}
      svgNode('text',{x:350,y:310,'text-anchor':'middle'},svg,v.x_label);create('p',(scale.fixed?'Fixed scale: ':'Current scale: ')+format(lo)+' to '+format(hi)+' '+unit(output.units),parent).className='scale-caption';
      svgNode('text',{transform:'translate(18 150) rotate(-90)','text-anchor':'middle'},svg,v.y_label);numericTable(value,output.label+' ('+unit(output.units)+')',tableDisclosure(parent),v.labels,tableAxes);return;
    }
    if(v.kind==='bar') {
      if(s.dims.length!==1)fail('Bar chart requires a vector');
      const svg=chart(v,parent),[lo,hi]=domain(value,true);axis(svg,v,1,value.length,lo,hi,'',output.units,true);
      const y=x=>284-(x-lo)/(hi-lo)*240,zero=y(0),width=510/value.length;
      value.forEach((x,i)=>{svgNode('rect',{x:92+i*width,y:Math.min(zero,y(x)),width:Math.max(1,width-8),height:Math.abs(y(x)-zero),fill:'#207a96'},svg);svgNode('text',{x:92+(i+.5)*width,y:Math.max(38,Math.min(280,y(x)+(x<0?18:-7))),'text-anchor':'middle'},svg,format(x));const label=(v.labels&&v.labels[i])||String(i+1);const tick=svgNode('text',{x:92+(i+.5)*width,y:306,'text-anchor':'middle'},svg,label.length>10?label.slice(0,9)+'…':label);svgNode('title',{},tick,label);});
      numericTable(value,output.label+' ('+unit(output.units)+')',tableDisclosure(parent),v.labels,tableAxes);return;
    }
    if(v.kind==='line') {
      if(s.dims.length!==0)fail('Line chart requires a scalar output');
      const sw=v.sweep,control=spec.controls.find(c=>c.id===sw.control),points=[];
      for(let i=0;i<sw.points;i++){const x=i===sw.points-1?sw.max:sw.min+(sw.max-sw.min)*i/(sw.points-1),next=clone(inputs);next[sw.control]=x;const value=compute(validate(next),b)[v.output];if(!finite(value))fail('Sweep output must be scalar');points.push([x,value]);}
      const inSweep=inputs[sw.control]>=sw.min&&inputs[sw.control]<=sw.max;
      const svg=chart(v,parent),[lo,hi]=domain(points.map(p=>p[1]).concat(inSweep?[result[v.output]]:[]));axis(svg,v,sw.min,sw.max,lo,hi,control.units,output.units);
      svgNode('polyline',{points:points.map(([x,y])=>(88+(x-sw.min)/(sw.max-sw.min)*520)+','+(284-(y-lo)/(hi-lo)*240)).join(' '),fill:'none',stroke:'#207a96','stroke-width':3},svg);
      const currentX=inputs[sw.control],currentY=result[v.output];
      create('p','Sweep holds the other inputs fixed. Moving '+control.label+' selects a position on this curve; changing other inputs can change the curve.',parent).className='section-note';
      if(currentX<sw.min||currentX>sw.max)create('p','Current position hidden: '+control.label+' = '+format(currentX)+' '+unit(control.units)+' is outside the plotted sweep ('+format(sw.min)+' to '+format(sw.max)+' '+unit(control.units)+').',parent).className='line-position';
      else if(currentY<lo||currentY>hi)create('p','Current position hidden: current output '+format(currentY)+' '+unit(output.units)+' is outside the plotted vertical domain.',parent).className='line-position';
      else{
        const cx=88+(currentX-sw.min)/(sw.max-sw.min)*520,cy=284-(currentY-lo)/(hi-lo)*240;
        const label='Current: '+control.label+' = '+format(currentX)+' '+unit(control.units)+'; '+output.label+' = '+format(currentY)+' '+unit(output.units);
        svgNode('line',{x1:cx,x2:cx,y1:cy,y2:284,stroke:'#785514','stroke-dasharray':'4 3'},svg);
        const marker=svgNode('circle',{cx,cy,r:6,fill:'#fff',stroke:'#785514','stroke-width':3,'data-current-position':'true'},svg);svgNode('title',{},marker,label);
        svgNode('text',{x:cx+(cx>348?-10:10),y:cy+(cy<55?22:-12),'text-anchor':cx>348?'end':'start'},svg,'Current');
        create('p',label,parent).className='line-position';
      }
      numericTable(points,'Sweep: '+v.x_label+' ('+unit(control.units)+'), '+output.label+' ('+unit(output.units)+')',tableDisclosure(parent),undefined,{columns:[v.x_label+' ('+unit(control.units)+')',output.label+' ('+unit(output.units)+')']});return;
    }
    fail('Unsupported visual');
  }
  function tableDisclosure(parent){const details=create('details',undefined,parent);create('summary','Inspect numeric values',details);return details;}
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
    return failed;
  }
  function recalculate() {
    const b=NumericRuntime.budget(2000000);let result,containers;
    try{result=compute(state,NumericRuntime.budget());if(JSON.stringify(state)!==JSON.stringify(lastInputs)){previous=last;last=result;lastInputs=clone(state);}containers=renderOutputs(result);resultReadout(result,el('principal-result'));el('principal-result').removeAttribute('data-stale');el('outputs').removeAttribute('data-stale');el('result-status').textContent='';}
    catch(error){status('Calculation failed. '+error.message,true);el('principal-result').setAttribute('data-stale','true');el('outputs').setAttribute('data-stale','true');el('result-status').textContent=last?'Last valid result retained — stale for current inputs. Values, comparisons and plots below belong to the last successful inputs.':'No valid result available.';el('check-status').textContent='Degraded: current calculation failed; checks not run.';el('check-status').className='skip';el('checks').replaceChildren();return;}
    el('visuals').replaceChildren(el('outputs'));let visualFailures=0;
    for(const v of spec.visuals){const box=create('div',undefined,containers.get(v.output));box.className='chart';box.tabIndex=0;box.setAttribute('role','region');box.setAttribute('aria-label',v.title);try{renderVisual(v,result,state,b,box);}catch(error){visualFailures++;box.replaceChildren();create('h3',v.title,box);create('p','Visual unavailable: '+error.message,box).className='error';}}
    status(visualFailures?'Calculation valid; '+visualFailures+' visual(s) unavailable.':'',visualFailures>0);
    try{const failed=selfChecks(result,b);if(failed){status('Calculation completed; '+failed+' scientific check(s) failed.'+(visualFailures?' '+visualFailures+' visual(s) unavailable.':''));el('status').className='caution';}}
    catch(error){el('check-status').textContent='Degraded: '+error.message;el('check-status').className='skip';status('Calculation completed; scientific checks unavailable.'+(visualFailures?' '+visualFailures+' visual(s) unavailable.':''));el('status').className='caution';}
  }
  if(data.error||!data.ast){status('Degraded: '+(data.error||'Compute unavailable'),true);el('check-status').textContent='Skipped: compute was not admitted.';document.querySelectorAll('.preset').forEach(button=>button.disabled=true);return;}
  try {
    state=merge({});controls();sync();
    document.querySelectorAll('.preset').forEach(button=>button.addEventListener('click',()=>{try{
      const index=Number(button.dataset.preset),next=merge(spec.explorations[index].preset);state=next;sync();recalculate();
      const readout=el('preset-result-'+index),feedback=el('feedback-'+index);
      if(feedback)feedback.open=false;
      if(readout){if(last&&el('result-status').textContent==='')resultReadout(last,readout,true);else readout.textContent='Preset applied, but calculation failed. See the workbench status.';}
    }catch(error){status('Invalid preset; last valid inputs retained. '+error.message,true);}}));
    recalculate();
  }catch(error){status('Degraded: '+error.message,true);el('check-status').textContent='Skipped: initialization failed.';}
})();
