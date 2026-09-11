<script>/* 星空滚动淡出：看板同款 data-scrolled 开关 */
addEventListener("scroll",function(){
  if(scrollY>40){document.documentElement.setAttribute("data-scrolled","");}
  else{document.documentElement.removeAttribute("data-scrolled");}
},{passive:true});</script>