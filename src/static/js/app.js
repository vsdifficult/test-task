// @ts-nocheck
// JavaScript for dynamic UI and WebSocket integration

document.addEventListener('DOMContentLoaded', () => {
    // TaskList creation code
    const createBtn = document.getElementById('create-tasklist-btn');
    const modal = document.getElementById('create-tasklist-modal');
    const cancelBtn = document.getElementById('cancel-create');
    const form = document.getElementById('create-tasklist-form');
    const taskListsUl = document.getElementById('task-lists');

    let isSubmittingTaskList = false;
    if (createBtn && modal && cancelBtn && form && taskListsUl) {
        createBtn.addEventListener('click', () => {
            modal.style.display = 'block';
        });

        cancelBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (isSubmittingTaskList) return;
            isSubmittingTaskList = true;
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            const name = form.name.value.trim();
            const description = form.description.value.trim();

            if (!name) {
                alert('Name is required');
                submitBtn.disabled = false;
                return;
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                const response = await fetch('/api/tasklists/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ name, description }),
                });

                if (response.ok) {
                    const data = await response.json();
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = `/list/${data.id}/`;
                    a.textContent = data.name;
                    li.appendChild(a);
                    taskListsUl.appendChild(li);
                    modal.style.display = 'none';
                    form.reset();
                    isSubmittingTaskList = false;
                    submitBtn.disabled = false;
                } else {
                    const errorData = await response.json();
                    alert('Error: ' + JSON.stringify(errorData));
                    isSubmittingTaskList = false;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                alert('Error: ' + error.message);
                isSubmittingTaskList = false;
                submitBtn.disabled = false;
            }
        });
    }

    // Task creation code
    const createTaskForm = document.getElementById('create-task-form');
    if (createTaskForm) {
        let isSubmittingTask = false;
        createTaskForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (isSubmittingTask) return;
            isSubmittingTask = true;
            const submitBtn = createTaskForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            const title = createTaskForm.title.value.trim();
            const description = createTaskForm.description.value.trim();
            const assigned_to_username = createTaskForm.assigned_to.value.trim();
            const due_date = createTaskForm.due_date.value;

            if (!title) {
                alert('Title is required');
                isSubmittingTask = false;
                submitBtn.disabled = false;
                return;
            }

            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                // Fetch user ID by username (assuming an API endpoint /api/users/?username=)
                let assigned_to_id = null;
                if (assigned_to_username) {
                    const userResp = await fetch(`/api/users/?username=${assigned_to_username}`, {
                        headers: { 'X-CSRFToken': csrfToken }
                    });
                    if (userResp.ok) {
                        const users = await userResp.json();
                        if (users.length > 0) {
                            assigned_to_id = users[0].id;
                        } else {
                            alert('Assigned user not found');
                            isSubmittingTask = false;
                            submitBtn.disabled = false;
                            return;
                        }
                    } else {
                        alert('Failed to fetch user info');
                        isSubmittingTask = false;
                        submitBtn.disabled = false;
                        return;
                    }
                }

                const taskData = {
                    title,
                    description,
                    due_date,
                    task_list: taskListId
                };
                if (assigned_to_id !== null) {
                    taskData.assigned_to_id = assigned_to_id;
                }

                const response = await fetch('/api/tasks/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify(taskData),
                });

                if (response.ok) {
                    const data = await response.json();
                    const tasksList = document.getElementById('tasks-list');
                    const li = document.createElement('li');
                    li.dataset.taskId = data.id;
                    li.innerHTML = `<strong>${data.title}</strong> - Assigned to: ${assigned_to_username || 'Unassigned'} - Due: ${data.due_date || 'N/A'} - Completed: <span class="completed-status">${data.completed ? 'Yes' : 'No'}</span> <button class="complete-btn" data-task-id="${data.id}">Mark Complete</button>`;
                    tasksList.appendChild(li);
                    createTaskForm.reset();
                    isSubmittingTask = false;
                    submitBtn.disabled = false;
                } else {
                    const errorData = await response.json();
                    alert('Error: ' + JSON.stringify(errorData));
                    isSubmittingTask = false;
                    submitBtn.disabled = false;
                }
            } catch (error) {
                alert('Error: ' + error.message);
                isSubmittingTask = false;
                submitBtn.disabled = false;
            }
        });
    }

    // Event delegation for complete buttons
    document.getElementById('tasks-list').addEventListener('click', async (e) => {
        if (e.target.classList.contains('complete-btn')) {
            const taskId = e.target.dataset.taskId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            try {
                const response = await fetch(`/api/tasks/${taskId}/`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ completed: true }),
                });
                if (response.ok) {
                    const li = e.target.closest('li');
                    li.querySelector('.completed-status').textContent = 'Yes';
                    e.target.remove();
                } else {
                    alert('Failed to mark task complete');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }
    });
});
