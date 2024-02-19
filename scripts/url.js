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

        // Function to modify the URL pathname
        function modifyURL() {
            // Get the current URL
            var url = new URL(window.location.href);

            // Get the pathname (part between the slashes)
            var pathname = url.pathname;

            // Modify the pathname as needed, in this case, just append "_modified"
            var modifiedPathname = pathname.replace(/\(.+?\)/, '(modified)');

            // Update the URL with the modified pathname
            url.pathname = modifiedPathname;

            // Update the URL with a random query parameter
            url.searchParams.set('query', generateRandomQuery());

            // Replace the current URL with the modified URL
            window.history.replaceState({}, '', url.toString());
        }

        // Call the function to modify the URL
        modifyURL();