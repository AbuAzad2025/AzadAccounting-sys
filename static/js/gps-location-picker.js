(function() {
    if (window.__GPS_LOCATION_PICKER_INIT__) return;
    window.__GPS_LOCATION_PICKER_INIT__ = true;

/**
 * GPS Location Picker - خرافي!
 * يتيح اختيار الموقع من خريطة Google Maps أو استخدام GPS الجهاز
 */

let map;
let marker;
let geocoder;

/**
 * تهيئة خريطة Google Maps
 */
function initLocationPicker(elementId, latInput, lngInput, addressInput) {
    const mapElement = document.getElementById(elementId);
    if (!mapElement) return;

    const defaultLat = parseFloat(latInput.value) || 31.9038;
    const defaultLng = parseFloat(lngInput.value) || 35.2034;
    const defaultPos = { lat: defaultLat, lng: defaultLng };

    map = new google.maps.Map(mapElement, {
        center: defaultPos,
        zoom: 15,
        mapTypeId: 'roadmap',
        streetViewControl: false,
        mapTypeControl: true,
        zoomControl: true,
        fullscreenControl: true
    });

    marker = new google.maps.Marker({
        position: defaultPos,
        map: map,
        draggable: true,
        animation: google.maps.Animation.DROP,
        title: 'اسحب لتغيير الموقع'
    });

    geocoder = new google.maps.Geocoder();

    marker.addListener('dragend', function(event) {
        const pos = event.latLng;
        updateInputs(pos.lat(), pos.lng(), latInput, lngInput, addressInput);
    });

    map.addListener('click', function(event) {
        const pos = event.latLng;
        marker.setPosition(pos);
        updateInputs(pos.lat(), pos.lng(), latInput, lngInput, addressInput);
    });

    const gpsButton = createGPSButton();
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(gpsButton);

    const shareButtons = createShareButtons(latInput, lngInput);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(shareButtons);

    const searchBox = createSearchBox();
    map.controls[google.maps.ControlPosition.TOP_LEFT].push(searchBox);

    const searchInput = searchBox.querySelector('input');
    const autocomplete = new google.maps.places.Autocomplete(searchInput, {
        componentRestrictions: { country: ['ps', 'il', 'jo'] }, // فلسطين، إسرائيل، الأردن
        fields: ['geometry', 'formatted_address', 'name']
    });

    autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        if (place.geometry) {
            const pos = place.geometry.location;
            map.setCenter(pos);
            map.setZoom(17);
            marker.setPosition(pos);
            updateInputs(pos.lat(), pos.lng(), latInput, lngInput, addressInput, place.formatted_address);
        }
    });
}

/**
 * تحديث حقول الإدخال
 */
function updateInputs(lat, lng, latInput, lngInput, addressInput, address = null) {
    latInput.value = lat.toFixed(6);
    lngInput.value = lng.toFixed(6);

    if (!address && addressInput) {
        geocoder.geocode({ location: { lat, lng } }, function(results, status) {
            if (status === 'OK' && results[0]) {
                addressInput.value = results[0].formatted_address;
            }
        });
    } else if (address && addressInput) {
        addressInput.value = address;
    }

    // تأثير بصري
    marker.setAnimation(google.maps.Animation.BOUNCE);
    setTimeout(() => marker.setAnimation(null), 750);
}

/**
 * إنشاء زر GPS
 */
function createGPSButton() {
    const controlDiv = document.createElement('div');
    controlDiv.style.padding = '10px';

    const button = document.createElement('button');
    button.className = 'btn btn-primary';
    button.innerHTML = '<i class="fas fa-crosshairs me-1"></i>استخدم موقعي الحالي';
    button.type = 'button';
    button.style.backgroundColor = '#fff';
    button.style.color = '#333';
    button.style.border = '2px solid #fff';
    button.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
    button.style.cursor = 'pointer';
    button.style.padding = '10px 15px';
    button.style.borderRadius = '8px';
    button.style.fontWeight = 'bold';

    button.addEventListener('click', function() {
        if (navigator.geolocation) {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>جاري التحديد...';

            const options = {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            };

            navigator.geolocation.getCurrentPosition(
                function(position) {
                    const pos = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    };

                    map.setCenter(pos);
                    map.setZoom(17);
                    marker.setPosition(pos);

                    const latInput = document.querySelector('input[name="geo_lat"]');
                    const lngInput = document.querySelector('input[name="geo_lng"]');
                    const addressInput = document.querySelector('input[name="address"]');
                    updateInputs(pos.lat, pos.lng, latInput, lngInput, addressInput);

                    button.disabled = false;
                    button.innerHTML = '<i class="fas fa-check-circle me-1 text-success"></i>تم التحديد!';
                    setTimeout(() => {
                        button.innerHTML = '<i class="fas fa-crosshairs me-1"></i>استخدم موقعي الحالي';
                    }, 2000);
                },
                function(error) {
                    
                    button.disabled = false;
                    button.innerHTML = '<i class="fas fa-times-circle me-1 text-danger"></i>فشل التحديد';
                    
                    let errorMsg = '❌ تعذر الحصول على موقعك.\n\n';
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMsg += '🔒 السبب: تم رفض الإذن للوصول للموقع.\n\n';
                            errorMsg += '✅ الحل:\n';
                            errorMsg += '1. انقر على أيقونة القفل 🔒 بجانب عنوان الموقع في المتصفح\n';
                            errorMsg += '2. ابحث عن "الموقع الجغرافي" أو "Location"\n';
                            errorMsg += '3. اختر "السماح" أو "Allow"\n';
                            errorMsg += '4. حدّث الصفحة وحاول مرة أخرى';
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMsg += '📡 السبب: لا يمكن تحديد الموقع حالياً.\n\n';
                            errorMsg += '✅ تأكد من:\n';
                            errorMsg += '- تفعيل GPS في جهازك\n';
                            errorMsg += '- الاتصال بالإنترنت\n';
                            errorMsg += '- عدم وجود تطبيقات تمنع الوصول للموقع';
                            break;
                        case error.TIMEOUT:
                            errorMsg += '⏱️ السبب: انتهت مهلة الانتظار.\n\n';
                            errorMsg += '✅ حاول مرة أخرى أو:\n';
                            errorMsg += '- تأكد من اتصالك بالإنترنت\n';
                            errorMsg += '- اذهب لمكان مفتوح لتحسين إشارة GPS';
                            break;
                    }
                    
                    alert(errorMsg);
                    
                    setTimeout(() => {
                        button.innerHTML = '<i class="fas fa-crosshairs me-1"></i>استخدم موقعي الحالي';
                    }, 3000);
                },
                options  // تمرير الخيارات
            );
        } else {
            alert('❌ المتصفح لا يدعم خدمات الموقع (GPS)');
        }
    });

    controlDiv.appendChild(button);
    return controlDiv;
}

window.initLocationPicker = initLocationPicker;

/**
 * إنشاء أزرار المشاركة والنسخ
 */
function createShareButtons(latInput, lngInput) {
    const controlDiv = document.createElement('div');
    controlDiv.style.padding = '10px';
    controlDiv.style.display = 'flex';
    controlDiv.style.gap = '10px';

    // زر نسخ الإحداثيات
    const copyButton = document.createElement('button');
    copyButton.className = 'btn btn-secondary';
    copyButton.innerHTML = '<i class="fas fa-copy me-1"></i>نسخ الموقع';
    copyButton.type = 'button';
    copyButton.style.backgroundColor = '#fff';
    copyButton.style.color = '#333';
    copyButton.style.border = '2px solid #fff';
    copyButton.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
    copyButton.style.cursor = 'pointer';
    copyButton.style.padding = '10px 15px';
    button_borderRadius = '8px';
    copyButton.style.fontWeight = 'bold';

    copyButton.addEventListener('click', function() {
        const lat = latInput.value;
        const lng = lngInput.value;
        
        if (!lat || !lng) {
            alert('⚠️ لم يتم تحديد موقع بعد!');
            return;
        }

        const formats = [
            `📍 الإحداثيات:`,
            `Latitude: ${lat}`,
            `Longitude: ${lng}`,
            ``,
            `🔗 Google Maps: https://www.google.com/maps?q=${lat},${lng}`,
            `🗺️ OpenStreetMap: https://www.openstreetmap.org/?mlat=${lat}&mlon=${lng}&zoom=15`
        ].join('\n');

        navigator.clipboard.writeText(formats).then(() => {
            copyButton.innerHTML = '<i class="fas fa-check-circle me-1 text-success"></i>تم النسخ!';
            setTimeout(() => {
                copyButton.innerHTML = '<i class="fas fa-copy me-1"></i>نسخ الموقع';
            }, 2000);
        }).catch(() => {
            const textarea = document.createElement('textarea');
            textarea.value = formats;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            
            copyButton.innerHTML = '<i class="fas fa-check-circle me-1 text-success"></i>تم النسخ!';
            setTimeout(() => {
                copyButton.innerHTML = '<i class="fas fa-copy me-1"></i>نسخ الموقع';
            }, 2000);
        });
    });

    // زر المشاركة
    const shareButton = document.createElement('button');
    shareButton.className = 'btn btn-success';
    shareButton.innerHTML = '<i class="fas fa-share-alt me-1"></i>مشاركة';
    shareButton.type = 'button';
    shareButton.style.backgroundColor = '#28a745';
    shareButton.style.color = '#fff';
    shareButton.style.border = '2px solid #fff';
    shareButton.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
    shareButton.style.cursor = 'pointer';
    shareButton.style.padding = '10px 15px';
    shareButton.style.borderRadius = '8px';
    shareButton.style.fontWeight = 'bold';

    shareButton.addEventListener('click', function() {
        const lat = latInput.value;
        const lng = lngInput.value;
        
        if (!lat || !lng) {
            alert('⚠️ لم يتم تحديد موقع بعد!');
            return;
        }

        const googleMapsUrl = `https://www.google.com/maps?q=${lat},${lng}`;
        const branchName = document.querySelector('input[name="name"]')?.value || 'الموقع';
        const shareText = `📍 موقع ${branchName}\n\n🗺️ عرض على الخريطة:\n${googleMapsUrl}`;

        if (navigator.share) {
            navigator.share({
                title: `موقع ${branchName}`,
                text: shareText,
                url: googleMapsUrl
            }).then(() => {
                shareButton.innerHTML = '<i class="fas fa-check-circle me-1"></i>تمت المشاركة!';
                setTimeout(() => {
                    shareButton.innerHTML = '<i class="fas fa-share-alt me-1"></i>مشاركة';
                }, 2000);
            }).catch((err) => {
                if (err.name !== 'AbortError') {
                    showShareModal(shareText, googleMapsUrl);
                }
            });
        } else {
            showShareModal(shareText, googleMapsUrl);
        }
    });

    controlDiv.appendChild(copyButton);
    controlDiv.appendChild(shareButton);
    return controlDiv;
}

/**
 * عرض نافذة المشاركة البديلة
 */
function showShareModal(text, url) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '50%';
    modal.style.left = '50%';
    modal.style.transform = 'translate(-50%, -50%)';
    modal.style.backgroundColor = '#fff';
    modal.style.padding = '30px';
    modal.style.borderRadius = '15px';
    modal.style.boxShadow = '0 10px 40px rgba(0,0,0,0.3)';
    modal.style.zIndex = '10000';
    modal.style.maxWidth = '500px';
    modal.style.width = '90%';
    modal.style.direction = 'rtl';

    modal.innerHTML = `
        <h4 style="margin-bottom: 20px; color: #333;">
            <i class="fas fa-share-alt me-2" style="color: #28a745;"></i>
            مشاركة الموقع
        </h4>
        <div style="margin-bottom: 20px;">
            <textarea readonly style="width: 100%; padding: 15px; border: 2px solid #ddd; border-radius: 8px; font-family: Arial; font-size: 14px; height: 150px; resize: none;">${text}</textarea>
        </div>
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <button onclick="window.open('https://wa.me/?text=' + encodeURIComponent('${text}'), '_blank')" style="background: #25D366; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                <i class="fab fa-whatsapp me-1"></i> واتساب
            </button>
            <button onclick="window.open('https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(text)}', '_blank')" style="background: #0088cc; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                <i class="fab fa-telegram me-1"></i> تيليجرام
            </button>
            <button onclick="window.open('mailto:?subject=موقع الفرع&body=${encodeURIComponent(text)}', '_blank')" style="background: #555; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                <i class="fas fa-envelope me-1"></i> بريد
            </button>
            <button onclick="this.closest('div').parentElement.parentElement.remove(); document.getElementById('modal-overlay').remove();" style="background: #dc3545; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                <i class="fas fa-times me-1"></i> إغلاق
            </button>
        </div>
    `;

    const overlay = document.createElement('div');
    overlay.id = 'modal-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.5)';
    overlay.style.zIndex = '9999';
    overlay.onclick = function() {
        modal.remove();
        overlay.remove();
    };

    document.body.appendChild(overlay);
    document.body.appendChild(modal);
}

/**
 * إنشاء صندوق البحث
 */
function createSearchBox() {
    const controlDiv = document.createElement('div');
    controlDiv.style.padding = '10px';

    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = '🔍 ابحث عن مكان...';
    input.style.width = '300px';
    input.style.padding = '10px 15px';
    input.style.border = '2px solid #fff';
    input.style.borderRadius = '8px';
    input.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
    input.style.fontSize = '14px';
    input.style.outline = 'none';

    controlDiv.appendChild(input);
    return controlDiv;
}

/**
 * تهيئة سريعة من HTML
 */
document.addEventListener('DOMContentLoaded', function() {
    if (!navigator.geolocation) {
    } else {
        const isSecure = window.location.protocol === 'https:' || 
                        window.location.hostname === 'localhost' || 
                        window.location.hostname === '127.0.0.1';
        
        if (navigator.permissions) {
            navigator.permissions.query({ name: 'geolocation' }).then(function(result) {
                if (result.state === 'denied') {
                } else if (result.state === 'granted') {
                } else {
                }
            }).catch(function(error) {
                
            });
        }
    }
    
    const mapElement = document.getElementById('location-map');
    if (mapElement) {
        const latInput = document.querySelector('input[name="geo_lat"]');
        const lngInput = document.querySelector('input[name="geo_lng"]');
        const addressInput = document.querySelector('input[name="address"]');
        
        if (latInput && lngInput) {
            if (typeof google === 'undefined') {
                const script = document.createElement('script');
                script.src = `https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places&language=ar&region=PS`;
                script.async = true;
                script.defer = true;
                script.onload = () => initLocationPicker('location-map', latInput, lngInput, addressInput);
                document.head.appendChild(script);
            } else {
                initLocationPicker('location-map', latInput, lngInput, addressInput);
            }
        }
    }
});

})();
