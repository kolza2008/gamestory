let openRequest = indexedDB.open('imperative_games', 1);
        console.log('БД работает')
        openRequest.onupgradeneeded = function(){
            let db = openRequest.result;
            db.createObjectStore('game_versions', {keyPath: 'id', autoIncrement: false});
            console.log('Версия ДБ обновлена')
        };
        openRequest.onerror = function(event){
            console.error(event);
        };