$(document).ready(function() {

   
    $('#searchBtn').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        getWeather();
        return false;
    });

  
    $('#cityInput').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            e.stopPropagation();
            getWeather();
            return false;
        }
    });

    function getWeather() {
        const city = $('#cityInput').val().trim();

        if (!city) {
            showError('Please enter a city name');
            return;
        }

        $('#errorMessage').addClass('d-none');
        $('#loadingSpinner').removeClass('d-none');

       
        $.ajax({
            url: 'http://localhost:5000/weather',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ city: city }),
            success: function(response) {
                $('#loadingSpinner').addClass('d-none');
                
                if (response.error) {
                    showError(response.error);
                } else {
                    displayWeather(response);
                }
            },
            error: function(xhr, status, error) {
                $('#loadingSpinner').addClass('d-none');
                showError('Failed to fetch weather data. Please try again.');
                console.error('Error:', error);
            }
        });
        
        return false;
    }

    function displayWeather(data) {
        $('.city-name').text(data.city);
        $('#temperature').text(data.temperature);
        $('#windSpeed').text(data.windSpeed);
        $('#windDirection').text(data.windDirection);
        $('#weatherTime').text(data.time);
        
        $('#weatherResult').removeClass('d-none');
    }

    function showError(message) {
        $('#errorMessage').text(message).removeClass('d-none');
    }
});