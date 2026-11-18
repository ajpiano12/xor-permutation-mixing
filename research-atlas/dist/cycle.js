(() => {
  const graph = document.querySelector("#cycle-graph");
  const p = [0, 2, 4, 6, 3, 1, 7, 5];
  const points = [null, [79,63], [122,27], [194,25], [250,65], [242,117], [175,141], [105,125]];
  const ns = "http://www.w3.org/2000/svg";
  const make = (tag, attrs, parent = graph) => {
    const el = document.createElementNS(ns, tag);
    Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v));
    parent.append(el);
    return el;
  };
  const defs = make("defs",{});
  for (const [id,fill] of [["arrow","#80b7af"],["current-arrow","#ffd986"]]) {
    const marker = make("marker",{id, markerWidth:7, markerHeight:7, refX:5, refY:3, orient:"auto", markerUnits:"userSpaceOnUse"},defs);
    make("path",{d:"M0 0 L6 3 L0 6",fill:"none",stroke:fill,"stroke-width":1.3},marker);
  }
  make("ellipse",{cx:165,cy:82,rx:100,ry:62,class:"guide"});
  make("ellipse",{cx:165,cy:82,rx:122,ry:73,class:"guide faint"});
  const edges = new Map(), nodes = new Map();
  for (let a = 1; a < p.length; a++) {
    const [x,y]=points[a], [u,v]=points[p[a]], length=Math.hypot(u-x,v-y);
    const dx=(u-x)/length, dy=(v-y)/length;
    edges.set(a,make("line",{x1:x+dx*7,y1:y+dy*7,x2:u-dx*9,y2:v-dy*9,class:"edge","marker-end":"url(#arrow)"}));
  }
  for (let a = 1; a < p.length; a++) {
    const [cx,cy]=points[a];
    const g = make("g",{class:"state"});
    make("circle",{cx,cy,r:8,class:"halo"},g);
    make("circle",{cx,cy,r:4,class:"node"},g);
    const x = cx+(cx<155?-14:14), y=cy+(cy<50?-7:cy>120?8:2);
    make("text",{x,y,"text-anchor":cx<155?"end":"start"},g).textContent = a.toString(2).padStart(3,"0");
    nodes.set(a,g);
  }
  let state=1, round=0;
  function draw() {
    nodes.forEach((g,a)=>g.classList.toggle("active",a===state));
    edges.forEach((line,a)=>{
      line.classList.toggle("active",a===state);
      line.setAttribute("marker-end", a===state?"url(#current-arrow)":"url(#arrow)");
    });
    document.querySelector("#cycle-readout").textContent = "Round "+round+" · difference "+state.toString(2).padStart(3,"0");
  }
  document.querySelector("#step-cycle").addEventListener("click",()=>{state=p[state];round++;draw();});
  draw();
  const snapshot = window.ATLAS?.snapshot;
  if(snapshot?.date) document.querySelector("#review-date").textContent = "Literature reviewed " + snapshot.date;
})();
