console.log("Yatrik JS Loaded");

document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    const searchResults = document.getElementById("search-results");

    if (searchInput && searchResults) {
        let timeout = null;
        
        searchInput.addEventListener("input", function(e) {
            clearTimeout(timeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                searchResults.innerHTML = "";
                return;
            }

            timeout = setTimeout(() => {
                fetch(`/api/temples/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        searchResults.innerHTML = "";
                        
                        if (data.length === 0) {
                            searchResults.innerHTML = `
                                <div class="alert alert-light text-center shadow-sm">
                                    No places found for "${query}". Try another search.
                                </div>
                            `;
                            return;
                        }

                        let html = '<div class="list-group shadow-sm text-start">';
                        data.forEach(item => {
                            const icon = item.type === 'temple' ? '🛕' : '📍';
                            html += `
                                <a href="${item.url}" class="list-group-item list-group-item-action d-flex align-items-center">
                                    <div class="me-3">
                                        <img src="/static/images/${item.image}" class="rounded" style="width:50px; height:50px; object-fit:cover;" alt="${item.name}">
                                    </div>
                                    <div>
                                        <h6 class="mb-0 fw-bold">${icon} ${item.name}</h6>
                                        <small class="text-muted">${item.city}</small>
                                    </div>
                                </a>
                            `;
                        });
                        html += '</div>';
                        searchResults.innerHTML = html;
                    })
                    .catch(err => {
                        console.error("Search error:", err);
                        searchResults.innerHTML = `
                            <div class="alert alert-danger text-center shadow-sm">
                                Error performing search. Please try again.
                            </div>
                        `;
                    });
            }, 300); // debounce
        });
    }
});