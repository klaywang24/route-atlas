/* 目录 */
(function(){
  var toc=document.getElementById('toc'),bk=document.getElementById('tocBack'),bt=document.getElementById('tocBtn');
  var items=[].slice.call(toc.querySelectorAll('.toc-item'));
  function close(){toc.classList.remove('open');bk.classList.remove('show');}
  bt.addEventListener('click',function(){toc.classList.toggle('open');bk.classList.toggle('show');});
  bk.addEventListener('click',close);
  items.forEach(function(a){a.addEventListener('click',close);});
  var hs=[].slice.call(document.querySelectorAll('[id^="s"]')).filter(function(e){return /^s\d$/.test(e.id);});
  function spy(){
    var cur=hs.length?hs[0].id:'';
    hs.forEach(function(h){ if(h.getBoundingClientRect().top<130) cur=h.id; });
    items.forEach(function(a){ a.classList.toggle('active',a.getAttribute('href')==='#'+cur); });
  }
  window.addEventListener('scroll',spy,{passive:true}); spy();
})();
