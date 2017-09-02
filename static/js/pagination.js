    var url=document.URL;
        var pag = document.getElementsByName("pagination");
        url = url.replace(/#/g,"");
        if(url.indexOf("?")==-1){
            for(var i=0;i<pag.length;i++){
                pag[i].href=url+"?pg="+pag[i].innerHTML;
            }
        }else{
            var str = location.search.substr(1); 
            strs = str.split("&");
            var search = "?";
            for (var i = 0; i < strs.length; i++) {
                if(strs[i].split("=")[0]!="pg"){
                    search=search+strs[i];
                }
            }
            if(search!="?") 
                search=search+"&";
            for(var i=0;i<pag.length;i++){
                pag[i].href=url.substring(0,url.indexOf("?"))+search+"pg="+pag[i].innerHTML;
            }
        }
