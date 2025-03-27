document.addEventListener('DOMContentLoaded', () => {
    
    document.querySelectorAll(".like-btn").forEach(button =>{
        button.addEventListener("click", () => {
            const postId = button.dataset.postId;

            fetch(`/like/${postId}`, {
                method: "PUT",
                headers: {
                    "X-CSRFToken":getCookie("csrftoken"),
                }
            })
            .then(response => response.json())
            .then(data => {
                document.querySelector(`#like-count-${postId}`).innerText = data.likes;
                button.innerText = button.innerText === "Like" ? "Unlike" : "Like";
            })
            .catch(err => console.log("Error: ",err));
            });
        });
    document.querySelectorAll(".edit-btn").forEach(button => {
        button.addEventListener("click", () => {
            console.log("Edit button clicked!");

            const postElement = button.closest(".post");
            const postId = button.dataset.postId;
            const contentElement = postElement.querySelector(".post-content");
            console.log("Post ID:", postId, "Content:", contentElement.innerText);

            if (button.innerText === "Edit") {
                console.log("Entering edit mode...");
                const oldContent = contentElement.innerText.trim();
                contentElement.innerHTML = `<textarea class="form-control edit-textarea">${oldContent}</textarea>`;
                button.innerText = "Save";
                button.classList.remove("btn-warning");
                button.classList.add("btn-success");
            } else if (button.innerText === "Save"){
                console.log("Saving content...");
                const newContent = contentElement.querySelector(".edit-textarea").value.trim();

                fetch(`/edit/${postId}`, {
                    method: "PUT",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        content: newContent,
                    })
                })

                .then(response => response.json())
                .then(data => {
                    console.log("Save response:", data);
                    if (data.error) {
                        alert(data.error);
                    }
                    else {
                        console.log("Post updated successfully!");
                        contentElement.innerHTML = newContent;
                        button.innerText = "Edit";
                        button.classList.remove("btn-success");
                        button.classList.add("btn-warning");
                    }
                })
                .catch(err => console.log("Error: ",err));
            }
         
        });    
    });
});

function getCookie(name){
    const CookieValue = document.cookie
    .split("; ")
    .find(row => row.startsWith(name))
    ?.split("=")[1];
    return CookieValue;
}