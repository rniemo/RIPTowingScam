function initMap() {

  var uluru = {lat: -25.363, lng: 131.044};
  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 4,
    center: uluru
  });

  var contentString = 'Ayy lmao';
  var infowindow = new google.maps.InfoWindow({
    content: contentString,
    maxWidth: 200
  });

  var marker = new google.maps.Marker({
    position: uluru,
    map: map,
    title: 'Uluru (Ayers Rock)'
  });

  marker.addListener('click', function() {
    infowindow.open(map, marker);
  });

  // Enter address
  document.getElementById('btn').onclick = function() {
    var geocoder = new google.maps.Geocoder();

    var search = document.getElementById('address').value;
    console.log(search);
    geocodeAddress(geocoder, map);
    map.setZoom(16);
  }

  // Didn't get towed
  document.getElementById('noTow').onclick = function() {
    var center = map.getCenter();
    var lat = center.lat();
    var lng = center.lng();
    console.log(lat + " " + lng);
  }

  // Got towed
  document.getElementById('gotTowed').onclick = function() {
    var center = map.getCenter();
    var lat = center.lat();
    var lng = center.lng();
    console.log(lat + " " + lng);
  }
}

function geocodeAddress(geocoder, resultsMap) {
  var address = document.getElementById('address').value;
  geocoder.geocode({'address': address}, function(results, status) {
    if (status === 'OK') {
      resultsMap.setCenter(results[0].geometry.location);
      myLoc = results[0].geometry.location;
      var ryan = resultsMap.getBounds();
      var NELat = ryan.getNorthEast().lat();
      var NELng = ryan.getNorthEast().lng();
      var SWLat = ryan.getSouthWest().lat();
      var SWLng = ryan.getSouthWest().lng();

      console.log(NELat + " " + NELng);
      console.log(SWLat + " " + SWLng);
      console.log(myLoc.lat() + " " + myLoc.lng());

      var marker = new google.maps.Marker({
        map: resultsMap,
        position: results[0].geometry.location
      });
    } else {
      alert('Geocode was not successful for the following reason: ' + status);
    }
  });
}