var d=document.documentElement;
try{var s=localStorage.getItem('fm-theme');if(s)d.setAttribute('data-theme',s);}catch(e){}
/* 切换＝看板同款（源=访客看板.html←klay-site theme-toggle.js）：旋转+圆形揭示；钥匙仍是 fm-theme */
(function(){var btn=document.getElementById('darkBtn');
function set(t){d.setAttribute('data-theme',t);try{localStorage.setItem('fm-theme',t);}catch(e){}}
btn.addEventListener('click',function(){
  var next=d.getAttribute('data-theme')==='dark'?'light':'dark';
  btn.classList.remove('spin');void btn.offsetWidth;btn.classList.add('spin');
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce||typeof document.startViewTransition!=='function'){set(next);return;}
  var r=btn.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
  var end=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y));
  document.startViewTransition(function(){set(next);}).ready.then(function(){
    d.animate({clipPath:['circle(0px at '+x+'px '+y+'px)','circle('+end+'px at '+x+'px '+y+'px)']},
      {duration:500,easing:'cubic-bezier(0.16, 1, 0.3, 1)',pseudoElement:'::view-transition-new(root)'});
  }).catch(function(){});
});})();