// auto close flashed messages 

$(document).ready(function () {
    setTimeout(function () {
        $(".alert").alert('close');
    }, 5000);
});


// edit comment
async function submitEditComment(event, comment_id) {
    event.preventDefault();
    const id = comment_id;
    const form = event.target;
    const formData = new FormData(form);
    try {
        const response = await fetch('/edit-comment/' + id, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            throw new Error('Network  response failed', response.statusText);
        }

        const result = await response.json();

        // hide form, display comment body
        const commentBody = document.getElementById('comment-body-' + id);
        const editForm = document.getElementById('edit-comment-form-' + id);

        if (commentBody.classList.contains('d-none')) {
            editForm.classList.add('d-none');
            commentBody.classList.remove('d-none');
            commentBody.innerText = result.text;
            // update toggle buttons dataset for reedit 
            toggle_btn = document.getElementById('toggleComment-' + id)
            toggle_btn.dataset.comment_body = result.text
        } else {
            editForm.classList.remove('d-none');
            commentBody.classList.add('d-none');
        }
        form.reset();
    }
    catch (error) {
        console.error('There was a problem:', error);
        alert('Failed to post!');
    }
};

// for submitting comments
async function postComment(event, post_id) {
    event.preventDefault();
    const post = event.target.dataset.post_id;
    const form = event.target;
    const formData = new FormData(form);
    try {
        const response = await fetch('/comment/' + post, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) {
            throw new Error('Network  response failed', response.statusText);
        }
        const result = await response.json();
        //  change posting comment style 
        if (result.html) {
            console.log('here')
            const commentContainer = document.getElementById(post_id + '-comments')
            commentContainer.insertAdjacentHTML('afterbegin', result.html)
        } else {
            throw new Error('Network  response failed', response.statusText);
        }
        form.reset();
        flask_moment_render_all();
    }
    catch (error) {
        console.error('There was a problem:', error);
        alert('Failed to post!')
    }
}

// toggle edit to post comment 
function toggleEditForm(event, id, body) {
    event.preventDefault();

    const commentBody = document.getElementById('comment-body-' + id);
    const editForm = document.getElementById('edit-comment-form-' + id);

    if (editForm.classList.contains('d-none')) {
        commentBody.classList.add('d-none');
        editForm.classList.remove('d-none');
        editForm[1].value = body;
    } else {
        editForm.classList.add('d-none');
        commentBody.classList.remove('d-none')
    }
}


//for translation
async function translate(source_Elem, dest_Elem, source_Lang, dest_lang) {
    document.getElementById(dest_Elem).innerHTML = "<img src=\"{{url_for('static', filename='loading.gif')}}\">";

    const response = await fetch('/translate', {
        method: "POST",
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({
            text: document.getElementById(source_Elem).innerText,
            source_language: source_Lang,
            dest_language: dest_lang
        })
    })
    const data = await response.json();
    console.log(data)
    document.getElementById(dest_Elem).innerHTML = "<p></p>"
    document.getElementById(dest_Elem).innerText = data.text;
}

//for tooltip popover
function initialize_popovers() {
    const popups = document.getElementsByClassName('user_popup');
    for (i = 0; i < popups.length; i++) {
        const popover = new bootstrap.Popover(popups[i], {
            content: 'loading...',
            trigger: 'hover focus',
            placement: 'right',
            html: true,
            sanitize: false,
            delay: { show: 500, hide: 0 },
            container: popups[i],
            customClass: 'd-inline',
        });
        popups[i].addEventListener('show.bs.popover', async (ev) => {

            if (ev.target.popupLoaded) {
                return;
            }

            const response = await fetch('/user-profile/' + ev.target.innerText.trim() + '/popup');
            const data = await response.text();
            const popover = bootstrap.Popover.getInstance(ev.target);
            if (popover && data) {
                ev.target.popupLoaded = true;
                popover.setContent({ '.popover-body': data });
                flask_moment_render_all();
            }
        });
    }
}
document.addEventListener('DOMContentLoaded', initialize_popovers);

//to set message count
function set_message_count(n) {
    const message_count = document.getElementById('message_count');
    message_count.innerText = n;
    message_count.style.visibility = n ? 'visible' : 'hidden';
}

//polling for notifications
{% if current_user.is_authenticated %}
function initialize_notifications() {
    let since = 0.0;

    // fetches notifications
    async function fetchNotifications() {
        const response = await fetch("{{url_for('main.notifications') }}?since=" + since);
        const notifications = await response.json();
        for (let i = 0; i <= notifications.length; i++) {
            switch (notifications[i].name) {
                case "unread_message_count":
                    set_message_count(notifications[i].data);
                    break;
                case "set_task_progress":
                    set_task_progress(notifications[i].data.task_id, notifications[i].data.progress);
                    break;
            }
            since = notifications[i].timestamp;
        }
    }
    // initial call to set notifications when any page is rendered
    fetchNotifications();
    setInterval(fetchNotifications, 10000); // call every 10 seconds
}

document.addEventListener('DOMContentLoaded', initialize_notifications);
{% endif %}

function set_task_progress(task_id, progress) {
    const progress_element = document.getElementById(task_id + '-progress')
    const progress_div = document.getElementById(task_id + '-progress-div')
    if (progress_element) {
        console.log(progress_element)
        progress_element.innerText = progress;
        // progress_div.style.display = block;
    }
}

