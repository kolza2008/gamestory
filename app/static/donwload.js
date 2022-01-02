let donwload = function(obj){
    ym(87008523,'reachGoal','donwload_game');
    let db = openRequest.result;
    let new_game_transaction = db.transaction('game_versions', 'readwrite');
    let store = new_game_transaction.objectStore("game_versions");
    let request = store.put(obj)
    request.onsuccess = function() { // (4)
        console.log("Версия сохранена", request.result);
    };
    request.onerror = function() {
        console.log("Ошибка", request.error);
    };
};