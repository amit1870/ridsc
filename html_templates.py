# -*- coding: utf8 -*-


def black_page(filepath,settings,div_dic):
    html = """<html>
  <head>
    <style>
      body {
      	display:table;
        background:{main_bg} center no-repeat ;
      }
      
      #P,#S,#T {
        position:absolute;
        overflow:hidden;
        background:{main_bg} center no-repeat;
      }

      #P {
        height:{P_div_h}px;
        width:{P_div_w}px;
        top:{P_div_t}px;
        left:{P_div_l}px;
        border-right: {border_width_v}px {sidebar_bg} solid;
        border-bottom: {border_width_h}px {sidebar_bg} solid;
      }
      #S {
        height:{S_div_h}px;
        width:{S_div_w}px;
        top:{S_div_t}px;
        left:{S_div_l}px;
        border-bottom: {border_width_v}px {sidebar_bg} solid;
        border-right: {border_width_h}px {sidebar_bg} solid;
      }

      #T {
        height:{T_div_h}px;
        width:{T_div_w}px;
        top:{T_div_t}px;
        left:{T_div_l}px;
        border-top: {border_width_v}px {sidebar_bg} solid;
        border-left: {border_width_h}px {sidebar_bg} solid;
       }
      #B {
        position:absolute;
        top:{logo_y}px;
        left:{logo_x}px;
      }
      #B img {
        max-width:100%;
        max-height:100%;
      }
      #status {
        position:absolute;
        left:{status_x}px;
        top:{status_y}px;
      } 
    </style>
    <script src="file:////home/pi/ridsc/static/client/setimg.js" type="text/javascript"></script> 
  </head>
  <body >

    <div id="P"></div>
    <div id="S"></div>
    <div id="T"></div>
    <div id="B"><img src="file:///{rids_logo}"/></div>
    <div id="status"><img id='ST' src="file:///home/pi/ridsc/static/img/on.png"/></div>

  </body>
</html>"""
    html = replace_all(html,settings)
    html = replace_all(html,div_dic)

    with open(filepath, 'w') as f:
        f.write(html)
    return filepath

def replace_all(html, dic):
    for k, v in dic.iteritems():
      html = html.replace('{'+k+'}', str(v))
    return html

def ticker_sidebar_page(filepath,settings,div_dic,spec):
    html = """<html>
  <head>
    <link href='file:////home/pi/ridsc/static/client/ticker_sidebar.css' rel='stylesheet' type='text/css'>
    <script src="file:////home/pi/ridsc/static/client/clock.js" type="text/javascript"></script>
    <style type="text/css">
            @font-face {
                font-family: 'myFont';
                src: url('file:////home/pi/ridsc/static/font/{ticker_font}');
            } 
            @font-face {
                font-family: 'mysideFont';
                src: url('file:////home/pi/ridsc/static/font/{sidebar_font}');
            } 
            #sidebar_wrapper{
              width:{sidebar_w}px;
              height:{sidebar_h}px;
              background-color: {sidebar_bg};
            }
            
            .ticker {
                background-color:{ticker_bg};
                color: {ticker_color};
                font-family:'myFont';
                font-size: {ticker_font_size};
            }
            #tickr_wrapper{
                background-color:{ticker_bg};
                top:{ticker_y}px;
                height:{ticker_h}px;
            }
            #tickr_content_wrapper{
                margin-top:{ticker_margin}px;
            }
            #event{
              font-family:'mysideFont';
              font-size:{sidebar_font_size};
              color:{sidebar_color};
            }
            #clock_wrapper {
              color:{sidebar_color};
            }
            #clock{
              border-top: 1px solid {sidebar_color};
            }
            
        </style>
        <script>
            function fitToDiv(font_Size){
              var event_div_h = document.getElementById('event').clientHeight;
              var event_div_w = document.getElementById('event').clientWidth;
              while (event_div_h > {event}) {
                  font_Size = font_Size - 2;
                  document.getElementById('event').style.fontSize = font_Size.toString() + 'px';
                  event_div_h = document.getElementById('event').clientHeight;                  
                  event_div_w = document.getElementById('event').clientWidth;                  

              };
              while (event_div_w > {sidebar_w}) {
                  font_Size = font_Size - 1;
                  document.getElementById('event').style.fontSize = font_Size.toString() + 'px';
                  event_div_w = document.getElementById('event').clientWidth;                  

              };

            }

            var clk_format = '{clock_format}' ;
            var events = [];
            var len = 0;
            var i = 0;

            function show_event(i){    
              if(len!=0){
                i=i%len;
                document.getElementById("event").innerHTML =  events[i];
                fitToDiv({sidebar_font_size});
              }     
              handle = setTimeout("show_event("+(i+1)+")",1000*{default_duration});
            }

            // if there is only sidebar
            window.set_sidebar = function(sidebar){
              events = sidebar.split("<|>");     
              i=0;
              len = events.length;
            }

            // if there is only ticker
            window.set_ticker = function(ticker){
              document.getElementById("tickr_content").innerHTML = "<marquee scrollamount={ticker_speed}>" + ticker +
                                                                   "<span class='star'> &nbsp;*&nbsp; </span>" + ticker + "</marquee>";     
            }

            // if both sidebar and ticker
            window.set_sidebar_ticker = function (sidebar,ticker) {
              document.getElementById("tickr_content").innerHTML = "<marquee scrollamount={ticker_speed}>" + ticker +
                                                                   "<span class='star'> &nbsp;*&nbsp; </span>" + ticker + "</marquee>";     
              events = sidebar.split("<|>");     
              i=0;
              len = events.length;
            }
        </script>
         
  </head>
  <body>  
    <div id="sidebar_wrapper">             
            <div id="logo_wrapper">
              <div ><img id="logo" src="file:///{institute_logo}"/></div>
            </div>
            <div id="event_wrapper">
                <div id="event">Add events to get displayed here and schedule those.</div>
            </div>
            <div id="clock_wrapper">
                <div id="clock"></div>
                <div id="day"></div>
                <div id="date"></div>
            </div>
    </div>
    <div id="tickr_wrapper" >             
        <div id="tickr_content_wrapper" class="ticker">
          <div id="tickr_content" style="white-space:nowrap"></div>
        </div>
    </div>
  </body>
  <script>
    clock();
    show_event(0);
  </script>
</html>"""
    html = replace_all(html,settings)
    html = replace_all(html,spec)
    html = replace_all(html,div_dic)

    with open(filepath, 'w') as f:
        f.write(html)
    return filepath


def splash_page(filepath,url,pi_id,settings):
    html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Welcome to RIDS</title>
    <link href='file:////home/pi/ridsc/static/css/bootstrap.css' rel='stylesheet' type='text/css'>
    <link href='file:////home/pi/ridsc/static/css/rids.css' rel='stylesheet' type='text/css'>
  </head>
  <body class="splash">
    <div class="container">
      <div class="row">
        <div class="span12">
          <div class="page-header text-center">
            <h1>Welcome to RIDS</h1>
          </div>
        </div>
      </div>
      <div class="row">
        <div class="span12 text-center"> """ 

    if settings['is_enabled']:
        html = html + """ <p class = "lead"> To manage the content on this screen <h2>""" + pi_id + """</h2></p>  <p class="lead">point your browser to <a href="http://app.rids.in">http://app.rids.in</a> </p> <br>"""
    else:
        html = html + """ <p class = "lead"> This screen is disabled, please contact administrator</p>"""

    html = html + url + """
        </div>
      </div>
      <hr/>
      <div class="row">
        <div class="span12 text-center">
          Brought to you by <br />
          <a href="http://rids.in">
            <img src="file:////home/pi/ridsc/static/img/rids_logo.png" />
          </a>
        </div>
      </div>
    </div>
  </body>
</html>
 
     """
    with open(filepath, 'w') as f:
        f.write(html)
    return filepath

