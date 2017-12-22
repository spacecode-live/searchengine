// favorites.js
function Favorite(num, latest, picid, num_favorites, latest_favorite) {
  var info = {
    num: num,
    latest: latest
  };
  this.element = info;
  this.picid = picid;
  this.element.num.value = num_favorites;
  this.element.latest.value = latest_favorite;
  num.addEventListener("change", this, false); 
}

Favorite.prototype.handleEvent = function(e) {
  if (e.type === "change") {
    this.update(this.element.value);
  }
}

Favorite.prototype.change = function(num_favorites, latest_favorite) {
  this.data = {
    'num_favor': num_favorites,
    'latest_favor': latest_favorite
  };
  this.num = num_favorites;
  this.latest = latest_favorite;
}

Favorite.prototype.update = function(username) {
  makeFavoritePostRequest(this.picid, username, function() {
    console.log('POST successful.');
  });
}

function makeFavoriteRequest(picid, cb) {
  qwest.get('/j89pws9vn291/pa3/pic/favorites?id=' + picid) 
    .then(function(xhr, resp) {
      cb(resp);
    });
}

function makeFavoritePostRequest(picid, username, cb) {
  var data = {
    'id': picid,
    'username': username
  };

  qwest.post('/j89pws9vn291/pa3/pic/favorites', data, {
    dataType: 'json',
    responseType: 'json'
  }).then(function(xhr, resp) {
    cb(resp);
  });
}

function userClick(picid, username) {
  makeFavoritePostRequest(picid, username, function() {
    console.log('User clicked like button. ');
  });
  makeFavoriteRequest(picid, function(resp) {
    document.getElementById("like").innerHTML = "Number of like " + resp['num_favorites'];
    document.getElementById("latest_like").innerHTML = "Latest favorited by " + resp['latest_favorite'];
  }); 
}

function initFavorite(picid) {
  var like = document.getElementById("like");
  var latest_like = document.getElementById("latest_like");
  var favoritBinding = new Favorite(like, latest_like, picid);

  makeFavoriteRequest(picid, function(resp) {
    favoriteBinding.change(resp['num_favorites'], resp['latest_favorite']);
  });

  setInterval(function() {
   makeFavoriteRequest(picid, function(resp) {
      like.innerHTML = "Number of like " + resp['num_favorites'];
      latest_like.innerHTML = "Latest favorited by " + resp['latest_favorite'];
      favoriteBinding.change(resp['num_favorites'], resp['latest_favorite']);
    }); 
  }, 10000);
}