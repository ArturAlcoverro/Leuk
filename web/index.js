let posts = document.getElementById("posts")
let bigImg = document.getElementById("big-img")
bigImg.onclick = () =>{
    bigImg.classList.remove("show")
}

console.log(posts);

function clickImg(url) {
    console.log(url);
    bigImg.style.backgroundImage = url
    bigImg.classList.add("show")
}

data.forEach(e => {
    let post = document.createElement("div")
    post.className = "post"


    let photos = document.createElement("div")
    photos.className = "photos"

    e["photos"].forEach(photo => {
        let img = document.createElement("div")
        let url = `url("../${photo}")`

        img.className = "photo"
        img.style.backgroundImage = url
        img.onclick = () => {clickImg(url)}
        photos.appendChild(img)
    })

    let comments = document.createElement("div")
    comments.className = "comments"

    e["comments"].forEach(comment => {
        let element = document.createElement("div")
        element.className = "comment"

        let username = document.createElement("p")
        username.className = "username"
        username.innerHTML = comment["user"]

        let text = document.createElement("p")
        text.className = "text"
        text.innerHTML = comment["text"]

        element.appendChild(username)
        element.appendChild(text)
        comments.appendChild(element)
    })

    if (e["comments"].length === 0) {
        let element = document.createElement("div")
        element.className = "comment"
        let text = document.createElement("p")
        text.className = "text"
        text.innerHTML = "---"
        
        element.appendChild(text)
        comments.appendChild(element)
    }

    post.appendChild(photos)
    post.appendChild(comments)

    posts.appendChild(post)
})

document.querySelectorAll(".photo")