/* Supplied source never reaches the host JS engine. All values live in this
   interpreter; host objects/functions cannot be obtained through properties. */
const NumericRuntime = (() => {
  const brand = Symbol('interpreter callable');
  const forbidden = new Set(['__proto__','prototype','constructor','caller','callee','arguments']);
  const mathNames = ['abs','sqrt','exp','log','log2','log10','pow','min','max','floor','ceil','round','trunc','sign','sin','cos','tan','tanh','expm1','log1p'];
  const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
  const fail = message => { throw new Error(message); };
  const number = v => typeof v === 'number' && Number.isFinite(v) ? v : fail('Expected a finite number');
  function budget(limit=100000) {
    return {left:limit, allocated:0, depth:0,
      tick(n=1){this.left-=n;if(this.left<0)fail('Computation instruction limit exceeded');},
      alloc(n){this.allocated+=n;if(this.allocated>16384)fail('Computation allocation limit exceeded');}};
  }
  function boundedArray(a,b) {
    if(a.length>128)fail('Intermediate array length limit is 128');
    b.alloc(a.length+1);return a;
  }
  const callable = run => ({[brand]:run});
  function invoke(fn,args,b) {
    b.tick();if(!fn || !own(fn,brand))fail('Only local or approved numeric functions may be called');
    if(++b.depth>32)fail('Computation call depth exceeded');
    try{return fn[brand](args,b);}finally{b.depth--;}
  }
  function environment(parent=null) {
    return {vars:Object.create(null),constants:new Set(),parent,
      get(k){if(own(this.vars,k))return this.vars[k];if(this.parent)return this.parent.get(k);fail('Unknown local: '+k);},
      set(k,v){if(own(this.vars,k)){if(this.constants.has(k))fail('Cannot reassign const: '+k);this.vars[k]=v;return v;}if(this.parent)return this.parent.set(k,v);fail('Unknown assignment: '+k);},
      declare(k,v,constant=false){if(own(this.vars,k))fail('Duplicate local: '+k);this.vars[k]=v;if(constant)this.constants.add(k);}};
  }
  function keyValue(key) {
    if(typeof key!=='string' && !(typeof key==='number' && Number.isInteger(key)))fail('Invalid property key');
    if(forbidden.has(String(key)))fail('Unsafe property access');return key;
  }
  function get(obj,key,b) {
    key=keyValue(key);b.tick();
    if(obj && own(obj,brand)){
      if(key==='apply'||key==='call')fail('Function .apply/.call is unsupported; call the function directly. For a numeric array use Math.max(...values), Math.min(...values), or a bounded loop.');
      fail('Functions have no accessible properties');
    }
    if(Array.isArray(obj)) {
      if(key==='length')return obj.length;
      if(Number.isInteger(key) && key>=0 && key<obj.length)return obj[key];
      const methods={
        map(args,b){if(args.length!==1)fail('map requires one callback');return boundedArray(obj.map((v,i)=>{b.tick();return invoke(args[0],[v,i],b);}),b);},
        forEach(args,b){if(args.length!==1)fail('forEach requires one callback');obj.forEach((v,i)=>{b.tick();invoke(args[0],[v,i],b);});return null;},
        reduce(args,b){if(args.length<1||args.length>2)fail('Invalid reduce arguments');if(!obj.length&&args.length===1)fail('Empty reduce without initial value');let acc=args.length===2?args[1]:obj[0];for(let i=args.length===2?0:1;i<obj.length;i++){b.tick();acc=invoke(args[0],[acc,obj[i],i],b);}return acc;},
        slice(args,b){if(args.length>2)fail('Invalid slice arguments');args.forEach(number);return boundedArray(obj.slice(...args),b);},
        fill(args,b){if(args.length!==1)fail('fill requires one value');b.tick(obj.length);obj.fill(args[0]);return obj;},
        push(args,b){if(obj.length+args.length>128)fail('Intermediate array length limit is 128');b.alloc(args.length);return obj.push(...args);},
        concat(args,b){const n=obj.length+args.reduce((s,x)=>s+(Array.isArray(x)?x.length:1),0);if(n>128)fail('Intermediate array length limit is 128');return boundedArray(obj.concat(...args),b);}
      };
      if(own(methods,key))return callable(methods[key]);
      fail('Unsupported array property: '+String(key));
    }
    if(obj && typeof obj==='object' && Object.getPrototypeOf(obj)===null && own(obj,key))return obj[key];
    fail('Missing or unsupported property: '+String(key));
  }
  function set(obj,key,value,b) {
    key=keyValue(key);b.tick();
    if(Array.isArray(obj) && Number.isInteger(key) && key>=0 && key<obj.length){obj[key]=value;return value;}
    if(obj && typeof obj==='object' && Object.getPrototypeOf(obj)===null && own(obj,key)){obj[key]=value;return value;}
    fail('Assignment may only replace an existing local value');
  }
  function binary(op,a,c) {
    if(op==='==='||op==='!==')return op==='==='?a===c:a!==c;
    a=number(a);c=number(c);
    switch(op){case '+':return number(a+c);case '-':return number(a-c);case '*':return number(a*c);
      case '/':return number(a/c);case '%':return number(a%c);case '**':return number(a**c);
      case '<':return a<c;case '>':return a>c;case '<=':return a<=c;case '>=':return a>=c;}
    fail('Unsupported operator');
  }
  function truth(v){if(typeof v==='boolean')return v;if(typeof v==='number')return number(v)!==0;if(v===null)return false;fail('Conditions must be numeric or boolean');}
  function expression(n,e,b) {
    b.tick();const k=n[0];
    if(k==='lit')return n[1];
    if(k==='id')return e.get(n[1]);
    if(k==='array')return boundedArray(n[1].map(v=>expression(v,e,b)),b);
    if(k==='object'){b.alloc(n[1].length+1);const o=Object.create(null);for(const [key,v] of n[1])o[key]=expression(v,e,b);return o;}
    if(k==='get')return get(expression(n[1],e,b),expression(n[2],e,b),b);
    if(k==='fn')return callable((args,b)=>{if(args.length<n[1].length)fail('Missing function argument');const local=environment(e);n[1].forEach((p,i)=>local.declare(p,args[i]));const r=statement(n[2],local,b);if(r&&r.type!=='return')fail('Loop control escaped function');return r?r.value:null;});
    if(k==='call') {
      const fn=expression(n[1],e,b),args=[];
      if(n[1][0]==='id'&&n[1][1]==='Number'&&(!fn||!own(fn,brand)))fail('Number(...) conversion is unsupported. Select inputs are strings: compare each option with === and return its numeric literal, or use a numeric control. Number.isFinite and Number.isInteger are supported.');
      for(const a of n[2]){if(a[0]==='spread'){const v=expression(a[1],e,b);if(!Array.isArray(v))fail('Spread requires array');args.push(...v);}else args.push(expression(a,e,b));if(args.length>128)fail('Argument limit exceeded');}
      return invoke(fn,args,b);
    }
    if(k==='un'){const v=expression(n[2],e,b);if(n[1]==='!')return !truth(v);return n[1]==='-'?-number(v):number(v);}
    if(k==='cond')return expression(truth(expression(n[1],e,b))?n[2]:n[3],e,b);
    if(k==='bin') {
      const a=expression(n[2],e,b);
      if(n[1]==='&&')return truth(a)?expression(n[3],e,b):a;
      if(n[1]==='||')return truth(a)?a:expression(n[3],e,b);
      return binary(n[1],a,expression(n[3],e,b));
    }
    if(k==='assign'||k==='update') {
      const target=n[2];let read,write;
      if(target[0]==='id'){read=()=>e.get(target[1]);write=v=>e.set(target[1],v);}
      else{const obj=expression(target[1],e,b),key=expression(target[2],e,b);read=()=>get(obj,key,b);write=v=>set(obj,key,v,b);}
      if(k==='update'){const old=number(read());write(number(old+(n[1]==='++'?1:-1)));return old;}
      const old=n[1]==='='?null:read(),value=expression(n[3],e,b);return write(n[1]==='='?value:binary(n[1][0],old,value));
    }
    fail('Unsupported AST expression');
  }
  function statement(n,e,b) {
    b.tick();const k=n[0];
    if(k==='block'){const local=environment(e);for(const s of n[1]){const r=statement(s,local,b);if(r)return r;}return null;}
    if(k==='decl'){for(const [name,v] of n[1])e.declare(name,expression(v,e,b),n[2]==='const');return null;}
    if(k==='expr'){expression(n[1],e,b);return null;}
    if(k==='return')return {type:'return',value:expression(n[1],e,b)};
    if(k==='throw'){
      const value=expression(n[1],e,b);
      // Never coerce a compound value: shared/cyclic arrays can expand without
      // bound inside native String(), outside the interpreter's work budget.
      const message=value===null?'null':typeof value==='string'?value.slice(0,1024):
        typeof value==='number'||typeof value==='boolean'?String(value):'non-scalar error value';
      fail('Compute reported: '+message);
    }
    if(k==='if')return statement(truth(expression(n[1],e,b))?n[2]:n[3],e,b);
    if(k==='break'||k==='continue')return {type:k};
    if(k==='for') {
      let local=environment(e);statement(n[1],local,b);let loops=0;
      while(truth(expression(n[2],local,b))){
        if(++loops>256)fail('Loop iteration limit exceeded');const r=statement(n[4],local,b);
        if(r&&r.type==='return')return r;if(r&&r.type==='break')break;
        // Lexical loop bindings are fresh for each iteration. Closures keep
        // the completed iteration's bindings, before the next increment.
        const next=environment(e),keys=Object.keys(local.vars);b.alloc(keys.length);
        for(const key of keys)next.declare(key,local.vars[key],local.constants.has(key));
        local=next;expression(n[3],local,b);
      }return null;
    }
    if(k==='each') {
      const seq=expression(n[2],e,b);if(!Array.isArray(seq)||seq.length>128)fail('for-of requires a bounded array');
      for(const value of seq){b.tick();const local=environment(e);local.declare(n[1],value,n[4]==='const');const r=statement(n[3],local,b);if(r&&r.type==='return')return r;if(r&&r.type==='break')break;}return null;
    }
    fail('Unsupported AST statement');
  }
  function copy(v,b,seen=new Set(),depth=0) {
    b.tick();if(depth>16)fail('Value nesting limit exceeded');
    if(v===null||['number','boolean','string'].includes(typeof v))return v;
    if(!v||typeof v!=='object'||own(v,brand)||seen.has(v))fail('Invalid or cyclic computation value');seen.add(v);
    let result;
    if(Array.isArray(v))result=boundedArray(v.map(x=>copy(x,b,seen,depth+1)),b);
    else {const keys=Object.keys(v);if(keys.length>128)fail('Object size limit exceeded');b.alloc(keys.length+1);result=Object.create(null);for(const k of keys){keyValue(k);result[k]=copy(v[k],b,seen,depth+1);}}
    seen.delete(v);return result;
  }
  function run(ast,inputs,shared=null) {
    const b=budget();
    if(shared){const tick=b.tick.bind(b);b.tick=function(n=1){tick(n);shared.tick(n);};}
    const root=environment(),math=Object.create(null),num=Object.create(null);
    for(const name of mathNames)math[name]=callable(args=>{if(args.length>128)fail('Math argument limit exceeded');args.forEach(number);return number(Math[name](...args));});
    math.PI=Math.PI;math.E=Math.E;
    num.isFinite=callable(args=>typeof args[0]==='number'&&Number.isFinite(args[0]));
    num.isInteger=callable(args=>typeof args[0]==='number'&&Number.isInteger(args[0]));
    const arr=callable((args,b)=>{if(args.length!==1)fail('Array requires one length');const n=number(args[0]);if(!Number.isInteger(n)||n<0||n>128)fail('Array length limit exceeded');return boundedArray(Array(n).fill(null),b);});
    root.declare('Math',math);root.declare('Number',num);root.declare('Array',arr);
    return copy(invoke(expression(ast,root,b),[copy(inputs,b)],b),b);
  }
  return Object.freeze({run,budget});
})();
