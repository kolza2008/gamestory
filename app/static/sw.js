self.addEventListener('push', function(event) {
  var message = JSON.parse(event.data.text()); //
  event.waitUntil(
    self.registration.showNotification(message.title, {
      body: message.body,
    })
  );
});