
var key = urlBase64ToUint8Array(document.getElementById('notify_key').content)//getKey()

function urlBase64ToUint8Array(base64String) {
    var padding = '='.repeat((4 - base64String.length % 4) % 4);
    var base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    var rawData = window.atob(base64);
    var outputArray = new Uint8Array(rawData.length);

    for (var i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
};

var sendSubscriptionToBackend = function(subscription){
    console.log(JSON.stringify(subscription));
    fetch('/subscribe', {'method':'post', 'body': JSON.stringify(subscription)})
    $.post('/subscribe',
           {'object':JSON.stringify(subscription)});
};

let subscribe = function(){
    // Проверка поддержки браузером уведомлений
    if (!("Notification" in window)) {
        alert("Ваш браузер не поддерживает уведомления");
        return;
    }
    // Проверка разрешения на отправку уведомлений
    else if (Notification.permission === "granted") {
        // Если разрешено, то создаём уведомление
        var notification = new Notification("Все ок!");
    }
    // В противном случае, запрашиваем разрешение
    else if (Notification.permission !== 'denied') {
        Notification.requestPermission(function (permission) {
        // Если пользователь разрешил, то создаём уведомление
        if (permission === "granted") {
            var notification = new Notification("Все ок!");
        } 
        else {
            return;
        }});
    };
    if (!('PushManager' in window)) {
        alert('Ваш браузер не поддерживает пуш-уведомления')
        return;
    };
    if(!('serviceWorker' in navigator)){
        alert('Ваш браузер не поддерживает фоновые задачи');
        return;
    };
    navigator.serviceWorker.register('/sw').then(
        function(registration){
            var subscribeOptions = {
                userVisibleOnly: true,
                applicationServerKey: key,
            };
            registration.pushManager.subscribe(subscribeOptions).then(subscription => sendSubscriptionToBackend(subscription)); 
        }
    );
};
 