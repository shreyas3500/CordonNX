var map;
  var markers = {};
  var geocoder;
  var addressCache = {};
  var lastZeroSpeedTime = {};
  var refreshInterval = 5000; // 1min for page reload
  var infoWindow;
  var countdownTimer = refreshInterval / 1000;
  var openMarker = null;
  var firstFit = true;
  var manualClose = false;
  var dataAvailable = true;
  var sosActiveMarkers = {};
var lastDataReceivedTime = {};
function restoreMarkers() {
const storedMarkers = sessionStorage.getItem('vehicleMarkers');
if (storedMarkers) {
    const markerData = JSON.parse(storedMarkers);
    markerData.forEach(device => {
        const latLng = new google.maps.LatLng(device.lat, device.lon);
        const imei = device.imei;
        const iconUrl = device.iconUrl;
        const rotation = device.rotation;
        markers[imei] = createCustomMarker(latLng, iconUrl, rotation);
        addMarkerClickListener(markers[imei], latLng, device);
    });
}
}
  function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 20.5937, lng: 78.9629 },
      zoom: 5,
      gestureHandling: "greedy",
      zoomControl: true,
      zoomControlOptions: {
        position: google.maps.ControlPosition.RIGHT_BOTTOM,
      },
    });
    geocoder = new google.maps.Geocoder();
    infoWindow = new google.maps.InfoWindow();
    google.maps.event.addListener(infoWindow, "closeclick", function () {
      const infoWindowDiv = document.querySelector(".info-window");
      if (infoWindowDiv) {
        infoWindowDiv.classList.remove("show");
        infoWindowDiv.classList.add("hide");
        setTimeout(function () {
          infoWindow.close();
        }, 300);
      }
      manualClose = true;
      openMarker = null;
    });
restoreMarkers();
    setInterval(function () {
      if (countdownTimer > 0) {
        countdownTimer--;
        document.getElementById("countdown").innerText = "Refresh in: " + countdownTimer + "s";
      } else {
    updateMap();
    countdownTimer = refreshInterval / 1000;  // Reset countdown
  }
}, 1000)};
function saveMarkers() {
const markerData = [];
Object.keys(markers).forEach(imei => {
    const marker = markers[imei];
    markerData.push({
        imei: imei,
        lat: marker.latLng.lat(),
        lon: marker.latLng.lng(),
        iconUrl: marker.div.style.backgroundImage.replace('url(', '').replace(')', ''),
        rotation: parseFloat(marker.div.style.transform.replace('rotate(', '').replace('deg)', ''))
    });
});
sessionStorage.setItem('vehicleMarkers', JSON.stringify(markerData));
}
  function parseCoordinates(lat, lon) {
    const parsedLat =
      parseFloat(lat.slice(0, 2)) + parseFloat(lat.slice(2)) / 60;
    const parsedLon =
      parseFloat(lon.slice(0, 3)) + parseFloat(lon.slice(3)) / 60;
    if (isNaN(parsedLat) || isNaN(parsedLon)) {
      console.error("Invalid coordinates:", lat, lon);
      return { lat: 0, lon: 0 };
    }
    return { lat: parsedLat, lon: parsedLon };
  }
  function convertSpeedToKmh(speedMph) {
    return speedMph * 1.60934; // Convert mph to km/h
  }
  function getCarIconUrlBySpeed(speedInKmh) {
    if (speedInKmh === 0) {
      return "http://64.227.135.38/cariconyellow.png";
    } else if (speedInKmh > 0 && speedInKmh <= 40) {
      return "http://64.227.135.38/caricongreen.png";
    } else if (speedInKmh > 40 && speedInKmh <= 60) {
      return "http://64.227.135.38/cariconblue.png";
    } else {
      return "http://64.227.135.38/cariconred.png";
    }
  }
function getCarIconBySpeed(speed, imei) {
    const speedInKmh = convertSpeedToKmh(speed);
    let iconUrl = getCarIconUrlBySpeed(speedInKmh);
    const now = new Date();
    if (speedInKmh === 0) {
        if (lastZeroSpeedTime[imei]) {
            const timeDiff = now - lastZeroSpeedTime[imei];
            const hoursDiff = timeDiff / (1000 * 60 * 60);
            if (hoursDiff >= 3) {
                iconUrl = "http://64.227.135.38/cariconblack.png";
            }
        } else {
            lastZeroSpeedTime[imei] = now; // Store the time when speed became 0
        }
    } else {
        delete lastZeroSpeedTime[imei];
    }
    return iconUrl;
}
function checkForDataTimeout(imei) {
    const now = new Date();
  const marker = markers[imei];
    if (lastDataReceivedTime[imei]) {
        const timeDiff = now - lastDataReceivedTime[imei];
        const hoursDiff = timeDiff / (1000 * 60 * 60);
        if (hoursDiff >= 1) {
      marker.div.style.border = "2px solid red";  
      marker.div.addEventListener("mouseover", function () {
        const tooltip = document.createElement("div");
        tooltip.className = "old-data-tooltip";
        tooltip.innerText = "Old data! New data not yet received";
        tooltip.style.position = "absolute";
        tooltip.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
        tooltip.style.color = "white";
        tooltip.style.padding = "5px";
        tooltip.style.borderRadius = "5px";
        tooltip.style.top = "-30px";  // Position tooltip above the marker
        tooltip.style.left = "50%";
        tooltip.style.transform = "translateX(-50%)";
        tooltip.style.zIndex = "1000";
        marker.div.appendChild(tooltip);
        marker.div.addEventListener("mouseout", function () {
          tooltip.remove();
        });
      });
    }
  }
}
  function animateMarker(marker, newPosition, duration = 6000) {
    const startPosition = marker.latLng;
    const startTime = performance.now();
    function moveMarker(currentTime) {
      const elapsedTime = currentTime - startTime;
      const progress = Math.min(elapsedTime / duration, 1);
      const lat =
        startPosition.lat() +
        (newPosition.lat() - startPosition.lat()) * progress;
      const lng =
        startPosition.lng() +
        (newPosition.lng() - startPosition.lng()) * progress;
      marker.latLng = new google.maps.LatLng(lat, lng);
      marker.draw();
      if (progress < 1) {
        requestAnimationFrame(moveMarker);
      }
    }
    requestAnimationFrame(moveMarker);
  }
  function sanitizeIMEI(imei) {
return imei.replace(/[^\w]/g, '').trim();  // Removes all non-alphanumeric characters
}
  function updateMap() {
    fetch("/api/data")
      .then((response) =>  response.json())
      .then((data) => {
        var imeiSet = new Set(); // Track unique IMEI numbers
        var bounds = new google.maps.LatLngBounds();
        dataAvailable = true;
        countdownTimer = refreshInterval / 1000;
        data.forEach((device) => {
          const imei = sanitizeIMEI(device.imei); 
          if (!imeiSet.has(imei)) {
            imeiSet.add(imei); // Mark IMEI as processed
          if (device.latitude && device.longitude && device.speed != null && device.course != null) {
            const coords = parseCoordinates(device.latitude, device.longitude);
            const latLng = new google.maps.LatLng(coords.lat, coords.lon);
            const iconUrl = getCarIconBySpeed(device.speed, imei);
            const rotation = device.course;
            if (markers[imei]) {
              animateMarker(markers[imei], latLng);
              updateCustomMarker(markers[imei], latLng, iconUrl, rotation);
              updateInfoWindow(markers[imei], latLng, device, coords);
            } else {
              markers[imei] = createCustomMarker(latLng, iconUrl, rotation);
              addMarkerClickListener(markers[imei], latLng, device, coords);
            }
            if (device.sos === "1") {
              triggerSOS(imei, markers[imei]);
            } else {
              removeSOS(imei);
            }
            lastDataReceivedTime[imei] = new Date();

            bounds.extend(latLng);
          }
           checkForDataTimeout(imei);
          }
        });
        saveMarkers();
        if (!bounds.isEmpty() && firstFit) {
          map.fitBounds(bounds);
          firstFit = false;
        }
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        dataAvailable = false;
      });
  }
  function triggerSOS(imei, marker) {
    if (!sosActiveMarkers[imei]) {
      const sosDiv = document.createElement("div");
      sosDiv.className = "sos-blink";
      marker.div.appendChild(sosDiv);
      sosActiveMarkers[imei] = sosDiv;
      setTimeout(() => {
        removeSOS(imei);
      }, 60000);
    }
  }
  function removeSOS(imei) {
    if (sosActiveMarkers[imei]) {
      sosActiveMarkers[imei].remove();
      delete sosActiveMarkers[imei];
    }
  }
  function formatDateTime(dateString, timeString) {
    const day = dateString.slice(0, 2);
    const month = dateString.slice(2, 4);
    const year = "20" + dateString.slice(4);
    let hour = parseInt(timeString.slice(0, 2), 10);
    const minute = timeString.slice(2, 4);
    const second = timeString.slice(4, 6);
    const ampm = hour >= 12 ? "PM" : "AM";
    hour = hour % 12 || 12;
    const formattedDate = ${day}/${month}/${year};
    const formattedTime = ${hour}:${minute}:${second} ${ampm};
    return { formattedDate, formattedTime };
  }
  function addMarkerClickListener(marker, latLng, device, coords) {
    geocodeLatLng(latLng, function (address) {
      marker.div.addEventListener("click", function () {
        if (openMarker !== marker) {
        const imei = device.imei
          ? device.imei
          : '<span class="missing-data">N/A</span>';
        const speed =
          device.speed !== null && device.speed !== undefined
            ? ${convertSpeedToKmh(device.speed).toFixed(2)} km/h
            : '<span class="missing-data">Unknown</span>';
        const lat =
          coords.lat !== null && coords.lat !== undefined
            ? coords.lat.toFixed(6)
            : '<span class="missing-data">Unknown</span>';
        const lon =
          coords.lon !== null && coords.lon !== undefined
            ? coords.lon.toFixed(6)
            : '<span class="missing-data">Unknown</span>';
        const date = device.date || "N/A";
        const time = device.time || "N/A";
        const addressText = address
          ? address
          : '<span class="missing-data">Location unknown</span>';
        const { formattedDate, formattedTime } = formatDateTime(date, time);
        const content = <div class="info-window show">
                <strong>IMEI:</strong> ${imei}<br>
                <hr>
                <p><strong>Speed:</strong> ${speed}</p>
                <p><strong>Lat:</strong> ${lat}</p>
                <p><strong>Lon:</strong> ${lon}</p>
                <p><strong>Last Update:</strong> ${formattedDate} ${formattedTime}</p> 
                <p class="address"><strong>Location:</strong> ${addressText}</p>
                <p><strong>Data:</strong> <a href="device-details.html?imei=${
                  device.imei || "N/A"
                }" target="_blank">View Data</a></p>
            </div>;
        if (openMarker !== marker) {
          infoWindow.setContent(content);
          infoWindow.setPosition(latLng);
          const infoWindowDiv = document.querySelector(".info-window");
          if (infoWindowDiv) {
            infoWindowDiv.classList.remove("hide");
            infoWindowDiv.classList.add("show");
          }
          infoWindow.open(map, marker);
          openMarker = marker;
          manualClose = false;
        }
      }
      });
    });
  }
  function updateInfoWindow(marker, latLng, device, coords) {
    geocodeLatLng(latLng, function (address) {
      if (openMarker === marker && !manualClose) {
        const { formattedDate, formattedTime } = formatDateTime(
          device.date,
          device.time
        );
        const content = <div class="info-window show">
                <strong>IMEI:</strong> ${device.imei}<br>
                <hr>
                <p><strong>Speed:</strong> ${convertSpeedToKmh(
                  device.speed
                ).toFixed(2)} km/h</p>
                <p><strong>Lat:</strong> ${coords.lat.toFixed(6)}</p>
                <p><strong>Lon:</strong> ${coords.lon.toFixed(6)}</p>
                <p><strong>Last Update:</strong> ${formattedDate} ${formattedTime}</p> 
                <p class="address"><strong>Location:</strong> ${address}</p>
                <p><strong>Data:</strong> <a href="device-details.html?imei=${
                  device.imei
                }" target="_blank">View Data</a></p>
            </div>;
        infoWindow.setContent(content);
        infoWindow.setPosition(latLng);
        infoWindow.open(map, marker);
      }
    });
  }
  function createCustomMarker(latLng, iconUrl, rotation) {
    const div = document.createElement("div");
    div.className = "custom-marker";
    div.style.backgroundImage = url(${iconUrl});
    div.style.transform = rotate(${rotation}deg);
    const marker = new google.maps.OverlayView();
    marker.div = div;
    marker.latLng = latLng;
    marker.onAdd = function () {
      const panes = this.getPanes();
      panes.overlayMouseTarget.appendChild(div);
    };
    marker.draw = function () {
      const point = this.getProjection().fromLatLngToDivPixel(this.latLng);
      if (point) {
        div.style.left = point.x - div.offsetWidth / 2 + "px";
        div.style.top = point.y - div.offsetHeight / 2 + "px";
      }
    };
    marker.onRemove = function () {
      div.parentNode.removeChild(div);
    };
    marker.setMap(map);
    addMarkerClickListener(marker, latLng, {}, {});
    return marker;
  }
  function updateCustomMarker(marker, latLng, iconUrl, rotation) {
    marker.latLng = latLng;
    marker.div.style.backgroundImage = url(${iconUrl});
    marker.div.style.transform = rotate(${rotation}deg);
    marker.draw();
    addMarkerClickListener(marker, latLng, {}, {});
  }
  function geocodeLatLng(latLng, callback) {
    const lat = latLng.lat().toFixed(6);
    const lon = latLng.lng().toFixed(6);
    const key = ${lat},${lon};
    if (addressCache[key]) {
      callback(addressCache[key]);
    } else {
      const geocodeUrl = https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lon}&key=AIzaSyCPEMAElTxMzur0DK-Mh3fPUVmdQVBJu8A;
      fetch(geocodeUrl)
        .then((response) => response.json())
        .then((data) => {
          if (data.status === "OK" && data.results[0]) {
            const address = data.results[0].formatted_address;
            addressCache[key] = address;
            callback(address);
          } else {
            callback("No address found");
          }
        })
        .catch((error) => {
          console.error("Error fetching geocode data:", error);
          callback("Error fetching address");
        });
    }
  }
  window.onload = initMap;
    <script
      src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCPEMAElTxMzur0DK-Mh3fPUVmdQVBJu8A&callback=initMap"
      async
    ></script>