const API_KEY = 'api_key=49e3be45df1c1a483b5eb9560e3c73ab';
const BASE_URL = 'https://api.themoviedb.org/3';
const IMAGE_URL = 'https://image.tmdb.org/t/p/w500';
// const FALLBACK_IMAGE = '/static/images/no-image.jpg';


const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const movieContainer = document.querySelector('.movie-container');

// Fetch Movies from API
async function getMovies(url) {
    try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.results) {
            displayMovies(data.results);
        }
    } catch (error) {
        console.error("Error fetching movies:", error);
    }
}

// Display Movies
function displayMovies(movies) {
    movieContainer.innerHTML = '';

    if (movies.length === 0) {
        movieContainer.innerHTML = `<p style="text-align:center;">No movies found.</p>`;
        return;
    }

    movies.forEach(movie => {
        const movieCard = document.createElement('div');
        movieCard.classList.add('movie-card');

        movieCard.innerHTML = `
            <img src="${movie.poster_path ? IMAGE_URL + movie.poster_path : FALLBACK_IMAGE}" 
                 alt="${movie.title}" 
                 class="movie-poster"
                 onerror="this.onerror=null;this.src='${FALLBACK_IMAGE}'">

            <div class="movie-info">
                <h3>${movie.title}</h3>
                <p>⭐ ${movie.vote_average}</p>
            </div>
        `;
        // Ensure each movie card has a click event listener
        movieCard.addEventListener('click', () => {
            window.location.href = `/movie/${movie.id}`; // Ensure this matches your Flask route
        });

        movieContainer.appendChild(movieCard);
    });
}

// Search Movie
searchButton.addEventListener("click", () => {
    const query = searchInput.value.trim();
    if (query) {
        getMovies(`${BASE_URL}/search/movie?${API_KEY}&query=${query}`);
    }
});

// Load Default Movies
getMovies(`${BASE_URL}/discover/movie?${API_KEY}`);

// Side Menu Toggle
const sideMenu = document.getElementById("side");

function showMenu() {
    sideMenu.classList.add("show");
}

function hideMenu() {
    sideMenu.classList.remove("show");
}
movieCard.addEventListener('click', () => {
    window.location.href = `movie_detail/${movie.id}`;
});
