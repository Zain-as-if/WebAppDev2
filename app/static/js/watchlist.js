$(document).ready(function() {
    $('#toggle-watchlist-btn').click(function() {
        var movieId = $(this).data('movie-id');
        console.log('Movie ID:', movieId);

        $.ajax({
            url: '/movie/' + movieId + '/toggle_watchlist',
            type: 'POST',
            success: function(response) {
                console.log('Response:', response);
                if (response && response.in_watchlist !== undefined) {
                    if (response.in_watchlist) {
                        $('#toggle-watchlist-btn').text('Remove from Watchlist');
                    } else {
                        $('#toggle-watchlist-btn').text('Add to Watchlist');
                    }
                } else {
                    alert('Unexpected response format');
                }
            },
            error: function(xhr, status, error) {
                console.log('Error: ', error);
                alert('Error while toggling the watchlist: ' + error);
            }
        });
    });
});
