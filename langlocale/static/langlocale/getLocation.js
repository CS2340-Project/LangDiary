function getLocation(){
    const data = {
        position: {
            'latitude': null,
            'longitude': null
        },
        status: false
    }
    const url = "";
    // const url = "{% url 'langlocale:index' %}";
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition((position) => {
            data.status = true;
            data.position.latitude = position.coords.latitude;
            data.position.longitude = position.coords.longitude;
        });
    }


    fetch(url, {
        method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
          },
          body: JSON.stringify(data)
    })
        .then((response) =>
          console.log(response)
        )
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
