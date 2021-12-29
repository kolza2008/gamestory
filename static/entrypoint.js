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
      }
    if(!('serviceWorker' in navigator)){
        alert('Ваш браузер не поддерживает фоновые задачи');
        return;
    };
    navigator.serviceWorker.register('/sw.js').then(()=>console.log('service worker loaded'));
    
};
 