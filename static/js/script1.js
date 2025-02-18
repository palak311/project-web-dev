// Script1 is script for Home(index.html) page 


var sideOption = document.getElementById("side");
function showMenu() {
    sideOption.style.left = "0";
}
function hideMenu() {
    sideOption.style.left = "-300px";
}


const API_KEY = 'api_key=49e3be45df1c1a483b5eb9560e3c73ab';
// const API_URL = 'https://api.themoviedb.org/3/movie/550?api_key=49e3be45df1c1a483b5eb9560e3c73ab';
const API_URL = `https://api.themoviedb.org/3/discover/movie?${API_KEY}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=1&with_watch_monetization_types=flatrate`;
// this is the image url of Api
const IMAGE_URL = 'https://image.tmdb.org/t/p/w500';

// we access Element by DOM Api and stores element in variable 
var container = document.getElementById('movies');
var search = document.getElementById('searchMovie');

var prevBtn = document.getElementById('prev-page');
var nextBtn = document.getElementById('next-page');


let pageNumber = 1;



apiCall(API_URL);

function apiCall(url) {
    
    const x = new XMLHttpRequest();
    x.open('get', url);
    x.send();
    
    x.onload = function () {
        container.innerHTML="";
        var res = x.response;
        
        var conJson = JSON.parse(res);
         
        var moviesArray = conJson.results;
         
        moviesArray.forEach(movie => moviesElement(movie));
        // addMovieToListButtonArray = document.getElementsByClassName('.add-movie-to-list');
    }
}


function moviesElement(movie) {
    var movieElement = document.createElement('div');
    movieElement.classList.add('movie-element');
    movieElement.innerHTML = `
    <a href="/movie/${movie.id}"><img src=${IMAGE_URL + movie.poster_path} alt="{movie.id}"></a>
    <div class="movie-info">
      <h3>${movie.title}</h3>
      <div class="star-fab">
      <div class="add-movie-to-list" id="${movie.id}" onclick="addMovie(${movie.id})">
      <span class="icon-color"><i class="fas fa-plus"></i></span>
      </div>
        <span class="icon-color"><i class="fa-solid fa-star">&nbsp;</i>${movie.vote_average}</span>
      </div>
    </div>
    <div class="overview">${movie.overview}</div>
    `;
    container.appendChild(movieElement);
}

// // array to store fav movies 
// var favMovies = [];
// // this old Movie list array kept previous local storage favorite Movie 
// var oldLocalsMov=[];

// // function to add movie to fav list 
// function addMovie(btnId){
//     document.getElementById(btnId).innerHTML = '<span class="icon-color"><i class="fas fa-check"></i></span>';
    // to avoid duplicate movies 
//     if(!favMovies.includes(btnId.toString())){
//         favMovies.push(btnId.toString());
//     }
     
//     oldLocalsMov = JSON.parse(localStorage.getItem('MovieArray'));
//     if(oldLocalsMov==null){
        
//         localStorage.setItem('MovieArray', JSON.stringify(favMovies));
//     }else{
//         // if not empty 
//         favMovies.forEach(item=>{
//             if(!oldLocalsMov.includes(item)){
//                 oldLocalsMov.push(item);
//             }
//         })
//         // adding the movie in local storage 
//         localStorage.setItem('MovieArray', JSON.stringify(oldLocalsMov));
//     }
// }



search.addEventListener('keyup', function(){
    var input = search.value;
    console.log(input)
    var inputUrl = `https://api.themoviedb.org/3/search/movie?${API_KEY}&query=${input}`;
    // https://api.themoviedb.org/3/search/movie?api_key={api_key}&query=Jack+Reacher
    if(input.length !=0){
        apiCall(inputUrl);
    }else{
        window.location.reload();
    }
})


prevBtn.disabled = true;
function disablePBtn() {
    if (pageNumber == 1) prevBtn.disabled = true;
    else prevBtn.disabled = false;
}


nextBtn.addEventListener('click', () => {
    pageNumber++;
    let tempURL = `https://api.themoviedb.org/3/discover/movie?${API_KEY}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=${pageNumber}&with_watch_monetization_types=flatrate`;
    apiCall(tempURL);
    disablePBtn();
});


prevBtn.addEventListener('click', () => {
    if (pageNumber == 1) return;

    pageNumber--;
    let tempURL = `https://api.themoviedb.org/3/discover/movie?${API_KEY}&language=en-US&sort_by=popularity.desc&include_adult=false&include_video=false&page=${pageNumber}&with_watch_monetization_types=flatrate`;
    apiCall(tempURL);
    disablePBtn();
})