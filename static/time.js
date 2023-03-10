function startTime(){
    var dateNow = new Date;
    var timeNow = document.getElementById("timeNow");
    var hours = dateNow.getHours();
    var minutes = dateNow.getMinutes();
    var seconds = dateNow.getSeconds();
    if(hours < 10)
            hours = "0" + hours
    if(minutes < 10)
            minutes = "0" + minutes
    if(seconds < 10)
            seconds = "0" + seconds

    var date = `${hours}:${minutes}:${seconds}`;
    timeNow.innerText = date;
}

setInterval(function() {
  startTime();
}, 1000);
