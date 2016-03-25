// Setting background of each divs 

window.setimg = function (uri,pl_id,ip) {
    var i = new Image();
    i.onload = function() {
      
      switch(pl_id){
        case "0":
            document.getElementById("P").style.backgroundSize = i.width > window.innerWidth || i.height > window.innerHeight ? 'contain' : 'auto';
            document.getElementById("P").style.backgroundImage = 'url(' + uri + ')';
            break;
        case "1":
            document.getElementById("S").style.backgroundSize = i.width > window.innerWidth || i.height > window.innerHeight ? 'contain' : 'auto';
            document.getElementById("S").style.backgroundImage = 'url(' + uri + ')';
            break;
        case "2":
            document.getElementById("T").style.backgroundSize = i.width > window.innerWidth || i.height > window.innerHeight ? 'contain' : 'auto';
            document.getElementById("T").style.backgroundImage = 'url(' + uri + ')';
            break;
      }
    }
    i.src = uri;
    
    ip != "0.0.0.0" ? document.getElementById("ST").src = 'file:///home/pi/ridsc/static/img/on.png' : document.getElementById("ST").src = 'file:///home/pi/ridsc/static/img/off.png';

}

// To clear the divs after video finishes

window.screen_black = function (pl_id,frame) {
    switch(pl_id){
        case "0":
            // document.getElementById("P").style.backgroundColor = '{main_bg}';
            document.getElementById("P").style.backgroundImage = "url('/home/pi/rids_files/"+frame.toString()+"')";
            document.getElementById("P").style.backgroundSize = "100% 100%";

            break;
        case "1":
            document.getElementById("S").style.backgroundImage = "url('/home/pi/rids_files/"+frame.toString()+"')";
            // document.getElementById("S").style.backgroundColor = '{main_bg}';
            document.getElementById("S").style.backgroundSize = "100% 100%";
            break;
        case "2":
            document.getElementById("T").style.backgroundImage = "url('/home/pi/rids_files/"+frame.toString()+"')";
            // document.getElementById("T").style.backgroundColor = '{main_bg}';
            document.getElementById("T").style.backgroundSize = "100% 100%";
            break;
    }

}

// Setting iframe to individual divs

window.set_iframe = function(uri,pl_id){
    switch(pl_id){
        case "0":
            var iframe = document.createElement('iframe');
            iframe.frameBorder = 0;
            iframe.scrolling = 'no';
            iframe.width = "100%";
            iframe.height = "100%";
            iframe.id = "randomid";
            iframe.setAttribute("src", uri+"/index.html?random=" + (new Date()).getTime());
            document.getElementById("P").appendChild(iframe);
            break;
        case "1":
            var iframe = document.createElement('iframe');
            iframe.frameBorder = 0;
            iframe.scrolling = 'no';
            iframe.width = "100%";
            iframe.height = "100%";
            iframe.id = "randomid";
            iframe.setAttribute("src", uri+"/index.html?random=" + (new Date()).getTime());
            document.getElementById("S").appendChild(iframe);        
            break;
        case "2":
            var iframe = document.createElement('iframe');
            iframe.frameBorder = 0;
            iframe.scrolling = 'no';
            iframe.width = "100%";
            iframe.height = "100%";
            iframe.id = "randomid";
            iframe.setAttribute("src", uri+"/index.html?random=" + (new Date()).getTime());
            document.getElementById("T").appendChild(iframe);        
            break;

      }

}

// To clear appended iframe tag to div's

window.iframe_clear = function(pl_id){
    switch(pl_id){
        case "0":
            if (document.getElementById("randomid")){
                document.getElementById("P").innerHTML = "";   
                document.getElementById("P").style.backgroundColor = '{main_bg}';
                document.getElementById("P").style.backgroundImage = 'none';
            } 
            break;
        case "1":
            if (document.getElementById("randomid")) {
                document.getElementById("S").innerHTML = "";
                document.getElementById("S").style.backgroundColor = '{main_bg}';
                document.getElementById("S").style.backgroundImage = 'none';
            }
            break;
        case "2":
            if (document.getElementById("randomid")) {
                document.getElementById("T").innerHTML = "";
                document.getElementById("T").style.backgroundColor = '{main_bg}';
                document.getElementById("T").style.backgroundImage = 'none';
            }
            break;
    }

}