import React, { useState, useEffect } from 'react';

// BUG: No PropTypes or TypeScript - no type safety

function TaskDashboard() {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');

    // BUG: useEffect with missing dependency array item
    useEffect(() => {
        fetchTasks();
    }, []); // BUG: if filter changes, tasks are not re-fetched

    // BUG: not handling component unmount (memory leak)
    const fetchTasks = async () => {
        try {
            const response = await fetch('/api/tasks');
            const data = await response.json(); // BUG: doesn't check response.ok first
            setTasks(data);
            setLoading(false);
        } catch (err) {
            setError(err.message);
            // BUG: loading is never set to false on error
        }
    };

    // BUG: function recreated on every render (should use useCallback)
    const handleDelete = async (id) => {
        // BUG: no confirmation dialog before delete
        await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
        // BUG: doesn't check if delete was successful
        // BUG: optimistic update without rollback on failure
        setTasks(tasks.filter(t => t.id !== id)); // BUG: stale closure over 'tasks'
    };

    const handleStatusChange = (id, newStatus) => {
        // BUG: mutating state directly
        const task = tasks.find(t => t.id === id);
        task.status = newStatus; // BUG: direct mutation of state object
        setTasks([...tasks]);
    };

    const handleBulkDelete = () => {
        const selectedIds = tasks
            .filter(t => t.selected)
            .map(t => t.id);
        
        // BUG: no check if selectedIds is empty
        fetch('/api/tasks/bulk-delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: selectedIds })
        });
        // BUG: not awaiting the promise
        // BUG: not updating local state after bulk delete
    };

    const filteredTasks = tasks.filter(t => {
        if (filter === 'all') return true;
        return t.status === filter;
    });

    // BUG: sorting mutates the array in place
    const sortedTasks = filteredTasks.sort((a, b) => b.createdAt - a.createdAt);

    if (loading) return <div>Loading...</div>; // BUG: no loading spinner or skeleton
    if (error) return <div>Error: {error}</div>; // BUG: no retry button

    return (
        <div className="dashboard">
            <h1>Task Dashboard</h1>
            
            {/* BUG: no key prop on select options */}
            <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                <option value="all">All Tasks</option>
                <option value="pending">Pending</option>
                <option value="in-progress">In Progress</option>
                <option value="completed">Completed</option>
            </select>

            <button onClick={handleBulkDelete}>Delete Selected</button>
            
            <div className="task-list">
                {sortedTasks.map((task, index) => (
                    // BUG: using index as key instead of task.id
                    <div key={index} className="task-card">
                        <input
                            type="checkbox"
                            checked={task.selected}
                            onChange={() => {
                                task.selected = !task.selected; // BUG: direct state mutation
                                setTasks([...tasks]);
                            }}
                        />
                        <h3 dangerouslySetInnerHTML={{ __html: task.title }} /> {/* BUG: XSS vulnerability */}
                        <p>{task.description}</p>
                        <span className={`priority-${task.priority}`}>
                            {task.priority}
                        </span>
                        
                        <select
                            value={task.status}
                            onChange={(e) => handleStatusChange(task.id, e.target.value)}
                        >
                            <option value="pending">Pending</option>
                            <option value="in-progress">In Progress</option>
                            <option value="completed">Completed</option>
                        </select>
                        
                        <button onClick={() => handleDelete(task.id)}>
                            Delete
                        </button>
                        
                        {/* BUG: no accessible labels, no aria attributes */}
                    </div>
                ))}
            </div>
            
            {/* BUG: shows "no tasks" even while loading */}
            {sortedTasks.length === 0 && <p>No tasks found</p>}
        </div>
    );
}

// BUG: Component for creating tasks - has uncontrolled/controlled input mix
function CreateTaskForm({ onSubmit }) {
    const [title, setTitle] = useState('');
    
    const handleSubmit = (e) => {
        e.preventDefault();
        
        // BUG: reading values directly from DOM instead of state
        const description = document.getElementById('description').value;
        const priority = document.getElementById('priority').value;
        
        onSubmit({ title, description, priority });
        
        // BUG: only resets title, not description or priority
        setTitle('');
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Task title"
            />
            {/* BUG: uncontrolled inputs mixed with controlled */}
            <textarea id="description" placeholder="Description" />
            <select id="priority">
                <option value="">Select Priority</option> {/* BUG: empty value can be submitted */}
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
            </select>
            <button type="submit">Create Task</button>
        </form>
    );
}

export default TaskDashboard;
