document.addEventListener('DOMContentLoaded', () => {
    const followBtn = document.querySelector("#follow-btn");
    
    if(!followBtn){
        console.error("Follow button not found");
        return;
    }

    followBtn.addEventListener("click", () => {
        const username = followBtn.getAttribute("data-username");

        if (!username) {
            console.error("Username not found!");
            return;
        }

                console.log("CSRF Token:", getCookie("csrftoken"))

        fetch(`/follow/${username}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json",
            },
            body: JSON.stringify({})
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            return response.json();
        })
        .then(data => {

                console.log("Server response:", data);

                if (data.error) {
                    alert(data.error);
                    return;
                }    

                document.querySelector("#followers-count").innerText = data.followers_count;
                followBtn.innerText = data.following_status ? "Unfollow" : "Follow";
    
                followBtn.classList.toggle("btn-primary", !data.following_status);
                followBtn.classList.toggle("btn-danger", data.following_status);
        })
        .catch(err=> console.error("error: ",err));
    });
});

function getCookie(name) {
    const cookieValue = document.cookie
        .split("; ")
        .find(row => row.startsWith(name))
        ?.split("=")[1];
    return cookieValue;
}