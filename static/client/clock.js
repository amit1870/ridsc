function pad(number) {
    if (number<=99) { number = ("0"+number).slice(-2); }
    return number;
}

function clock(){
    var d = new Date();
    var hour = d.getHours();  /* Returns the hour (from 0-23) */
    var minutes = d.getMinutes();  /* Returns the minutes (from 0-59) */
    var seconds = d.getSeconds();
    var days= ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
    var day = days[d.getDay()] ;
    var year = d.getFullYear() ;
    var date = d.getDate();
    var months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
    var month = months[d.getMonth()];
    var ext = '';
    // var clk_format = '{clock_format}' ;
    if(clk_format == '12'){    
        if(hour >= 12)
            ext = 'PM'                                     
        else 
            ext = 'AM';

        hour = hour%12;
        if(hour==0)
            hour ="12";                        
    }
    // result = pad(hour) + ":" + pad(minutes) + ":" + pad(seconds) + ' '+ext; 
    result = pad(hour) + ":" + pad(minutes) +' '+ext; 
    document.getElementById('clock').innerHTML = result;
    result = day
    document.getElementById('day').innerHTML = result;
    result = month + "&nbsp;" + date;
    document.getElementById('date').innerHTML = result;
    setTimeout('clock()',10000);
}   
