const pptx = new (require('pptxgenjs'))();
pptx.layout='LAYOUT_WIDE';
const INK="14251D", PAPER="F7F9F7", WHITE="FFFFFF", LINE="DCE4DF", MUTED="5E6E66",
      GREEN="2E9E6B", TEAL="2E8FA0", AMBER="D2892C", RED="C4553E", INKMUT="9DB4A9";
const HEAD="Cambria", BODY="Calibri";
function bg(s,c){s.background={color:c};}
function eyebrow(s,t,x,y,c){s.addText(t.toUpperCase(),{x,y,w:11,h:0.3,fontFace:BODY,fontSize:12,bold:true,color:c||TEAL,charSpacing:3});}
function title(s,t,x,y,w,c,sz){s.addText(t,{x,y,w:w||12,h:1.0,fontFace:HEAD,fontSize:sz||34,bold:true,color:c||INK,lineSpacingMultiple:0.98});}
function foot(s,t){s.addText(t,{x:0.6,y:7.08,w:12.1,h:0.3,fontFace:BODY,fontSize:9,color:MUTED});}
function stat(s,x,y,w,big,lab,ac){
  s.addShape('roundRect',{x,y,w,h:1.55,rectRadius:0.09,fill:{color:WHITE},line:{color:LINE,width:1},shadow:{type:'outer',color:'8A9A92',opacity:0.25,blur:8,offset:2,angle:90}});
  s.addText(big,{x:x+0.02,y:y+0.18,w:w-0.04,h:0.72,fontFace:HEAD,fontSize:28,bold:true,color:ac||INK,align:'center',margin:0});
  s.addText(lab,{x:x+0.14,y:y+0.94,w:w-0.28,h:0.55,fontFace:BODY,fontSize:12,color:MUTED,align:'center',margin:0,lineSpacingMultiple:1.0});
}

// ── Slide 1: title
let s=pptx.addSlide(); bg(s,INK);
s.addText("INDIA · VAHAN · 2026",{x:0.75,y:1.25,w:11,h:0.4,fontFace:BODY,fontSize:13,bold:true,color:GREEN,charSpacing:4});
s.addText("India's vehicle map",{x:0.72,y:1.85,w:11.8,h:1.2,fontFace:HEAD,fontSize:50,bold:true,color:WHITE});
s.addText("Where the fleet is — and how concentrated each fuel is",{x:0.75,y:3.05,w:11.8,h:0.7,fontFace:HEAD,fontSize:23,italic:true,color:TEAL});
s.addText([{text:"Six states hold half of India's ~18 million registrations. ",options:{bold:true,color:WHITE}},{text:"But some fuels — CNG above all — are far more concentrated than others.",options:{color:"D5E3DD"}}],{x:0.75,y:4.05,w:10,h:1,fontFace:BODY,fontSize:16,lineSpacingMultiple:1.15});
s.addText("Vahan4 dashboard · state × fuel · CY2026 year-to-date",{x:0.75,y:6.75,w:11.8,h:0.35,fontFace:BODY,fontSize:11,color:INKMUT});

// ── Slide 2: leaders
s=pptx.addSlide(); bg(s,PAPER);
eyebrow(s,"Who leads",0.6,0.55,TEAL);
title(s,"The five states that drive the aggregate",0.6,0.85);
stat(s,0.6,2.2,2.9,"47%","of all vehicles in the top 5 states",INK);
stat(s,3.65,2.2,2.9,"UP · Mah","biggest markets (13.7% · 10.9%)",GREEN);
stat(s,6.7,2.2,2.9,"6 states","to reach half the national fleet",AMBER);
stat(s,9.75,2.2,2.95,"71%","of all vehicles in the top 10",TEAL);
s.addShape('roundRect',{x:0.6,y:4.35,w:12.1,h:2.35,rectRadius:0.1,fill:{color:INK}});
s.addText("Who leads each type",{x:0.95,y:4.6,w:11,h:0.5,fontFace:HEAD,fontSize:19,bold:true,color:GREEN});
s.addText([
  {text:"By count:  ",options:{bold:true,color:AMBER}},
  {text:"UP leads total, petrol and EV (its EV lead is e-rickshaws) · Maharashtra leads diesel, CNG and strong hybrids.\n",options:{color:"D5E3DD"}},
  {text:"By share:  ",options:{bold:true,color:AMBER}},
  {text:"EV penetration highest in the east/northeast (Tripura, Assam ~17%, e-rickshaws) and Delhi (~12%); CNG highest in Haryana, Gujarat, Delhi — the mature CGD states.",options:{color:"D5E3DD"}}
],{x:0.95,y:5.15,w:11.3,h:1.4,fontFace:BODY,fontSize:15,lineSpacingMultiple:1.2});
foot(s,"Vahan4, CY2026 YTD, all 36 states/UTs. Absolute leaders differ from penetration leaders.");

// ── Slide 3: Lorenz / Pareto
s=pptx.addSlide(); bg(s,PAPER);
eyebrow(s,"Concentration",0.6,0.55,TEAL);
title(s,"CNG is far more concentrated than petrol",0.6,0.85);
s.addText("Cumulative share of each fuel held by the top-N states. The higher the curve, the more concentrated.",{x:0.6,y:1.75,w:12,h:0.4,fontFace:BODY,fontSize:14,color:MUTED});
const lab=["Top 1","5","10","15","20","25","30","All 36"];
const lz=[
  {name:"CNG",labels:lab,values:[17.6,64.4,89.5,97.0,99.6,99.9,100,100]},
  {name:"All vehicles",labels:lab,values:[13.7,47.0,71.0,86.9,97.1,99.0,99.7,100]},
  {name:"If evenly spread",labels:lab,values:[2.8,13.9,27.8,41.7,55.6,69.4,83.3,100]}
];
s.addChart(pptx.ChartType.line,lz,{x:0.5,y:2.3,w:8.6,h:4.4,
  chartColors:[AMBER,TEAL,INKMUT], lineSize:2.75, lineDataSymbol:"circle", lineDataSymbolSize:5,
  showTitle:false, showLegend:true, legendPos:"b", legendColor:INK, legendFontFace:BODY, legendFontSize:12,
  valAxisMinVal:0, valAxisMaxVal:100, valAxisLabelFormatCode:'0"%"',
  valAxisLabelColor:MUTED, valAxisLabelFontFace:BODY, valAxisLabelFontSize:10,
  catAxisLabelColor:INK, catAxisLabelFontFace:BODY, catAxisLabelFontSize:11,
  valGridLine:{color:LINE,size:1}, catGridLine:{style:"none"}});
s.addShape('roundRect',{x:9.35,y:2.3,w:3.4,h:4.4,rectRadius:0.09,fill:{color:INK}});
s.addText("The gap",{x:9.6,y:2.55,w:3,h:0.4,fontFace:HEAD,fontSize:19,bold:true,color:GREEN});
s.addText([
  {text:"The top 5 states hold ",options:{color:"D5E3DD"}},
  {text:"64% of CNG ",options:{bold:true,color:AMBER}},
  {text:"but only ",options:{color:"D5E3DD"}},
  {text:"47% of all vehicles. ",options:{bold:true,color:WHITE}},
  {text:"CNG clusters in the CGD-network states; petrol & diesel track population evenly. So CNG's fuel-substitution effect is regional — ethanol's is national.",options:{color:"D5E3DD"}}
],{x:9.6,y:3.15,w:2.9,h:3.4,fontFace:BODY,fontSize:14,lineSpacingMultiple:1.2});
foot(s,"Lorenz-style cumulative curve. Petrol ≈ 'all vehicles' (near-identical). HHI: CNG 1,056 vs petrol/total ~667. Vahan CY2026 YTD.");

pptx.writeFile({fileName:'/private/tmp/claude-501/-Users-umashankar/68d5bc86-4c5c-4205-abde-7dfbb1251c95/scratchpad/India_Vehicle_Distribution_2026.pptx'}).then(f=>console.log('WROTE',f));
