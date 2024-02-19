        // Function to generate a random query parameter
        function generateRandomQuery() {
            var query = '';
            var characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            var charactersLength = characters.length;
            for (var i = 0; i < 8; i++) {
                query += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return query;
        }

        // Function to generate a random path
        function generateRandomPath() {
            var path = '';
            var segments = ['products', 'services', 'about', 'contact'];
            var randomIndex = Math.floor(Math.random() * segments.length);
            path = '/' + segments[randomIndex];
            return path;
        }

        // Generate a new random query parameter and path on each page load
        var newQuery = generateRandomQuery();
        var newPath = generateRandomPath();

        // Update the URL with the new query parameter and path
        var url = new URL(window.location.href);
        url.searchParams.set('query', newQuery);
        url.pathname = newPath;
        window.history.replaceState({}, '', url.toString());