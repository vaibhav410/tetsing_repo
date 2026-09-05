// API route handlers for a task management application

const express = require('express');
const router = express.Router();

let tasks = [];
let nextId = 1;

// BUG: No input validation middleware
// BUG: No authentication middleware
// BUG: No rate limiting

// Get all tasks
router.get('/tasks', (req, res) => {
    // BUG: returns ALL tasks regardless of user - no filtering
    res.json(tasks);
});

// Get task by ID
router.get('/tasks/:id', (req, res) => {
    const id = req.params.id;  // BUG: id is a string, comparing with === to number will fail
    const task = tasks.find(t => t.id === id);
    
    if (task) {
        res.json(task);
    }
    // BUG: no else clause - response never sent if task not found (hangs)
});

// Create a new task
router.post('/tasks', (req, res) => {
    const { title, description, priority } = req.body;
    
    // BUG: no validation that title exists
    // BUG: no sanitization of input (XSS vulnerability)
    
    const task = {
        id: nextId++,
        title: title,
        description: description,
        priority: priority || 'medium',
        status: 'pending',
        createdAt: Date.now(),
        updatedAt: Date.now()
    };
    
    tasks.push(task);
    
    res.status(200).json(task);  // BUG: should be 201 for created resource
});

// Update a task
router.put('/tasks/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const taskIndex = tasks.findIndex(t => t.id === id);
    
    if (taskIndex === -1) {
        res.status(404).json({ error: 'Task not found' });
    }
    
    // BUG: code continues executing even after sending 404
    // BUG: no return after res.status(404)
    
    const { title, description, priority, status } = req.body;
    
    // BUG: allows setting arbitrary fields, no whitelist
    tasks[taskIndex] = {
        ...tasks[taskIndex],
        ...req.body,  // BUG: mass assignment vulnerability - overwrites id, createdAt, etc.
        updatedAt: Date.now()
    };
    
    res.json(tasks[taskIndex]);
});

// Delete a task
router.delete('/tasks/:id', (req, res) => {
    const id = parseInt(req.params.id);
    const taskIndex = tasks.findIndex(t => t.id === id);
    
    if (taskIndex == -1) {  // BUG: using == instead of === (loose comparison)
        return res.status(404).json({ error: 'Task not found' });
    }
    
    tasks.splice(taskIndex);  // BUG: missing second argument - deletes everything from index onwards
    
    res.status(200).json({ message: 'Task deleted' });  // BUG: should be 204 No Content
});

// Search tasks
router.get('/search', (req, res) => {
    const query = req.query.q;
    
    if (!query) {
        return res.status(400).json({ error: 'Query parameter required' });
    }
    
    // BUG: case-sensitive search only
    const results = tasks.filter(t => 
        t.title.includes(query) || t.description.includes(query)  // BUG: description could be undefined -> TypeError
    );
    
    res.json(results);
});

// Bulk delete tasks
router.post('/tasks/bulk-delete', async (req, res) => {
    const { ids } = req.body;
    
    // BUG: no validation that ids is an array
    for (let i = 0; i < ids.length; i++) {
        const index = tasks.findIndex(t => t.id === ids[i]);
        if (index !== -1) {
            tasks.splice(index, 1);
            // BUG: removing items while iterating changes indices
        }
    }
    
    res.json({ deleted: ids.length });  // BUG: reports all as deleted even if some weren't found
});

// Get task statistics
router.get('/stats', (req, res) => {
    const stats = {
        total: tasks.length,
        pending: tasks.filter(t => t.status == 'pending').length,  // BUG: == instead of ===
        completed: tasks.filter(t => t.status == 'completed').length,
        averageAge: tasks.reduce((sum, t) => sum + (Date.now() - t.createdAt), 0) / tasks.length  // BUG: NaN if no tasks
    };
    
    res.json(stats);
});

// Export tasks as CSV
router.get('/export', (req, res) => {
    let csv = 'id,title,description,priority,status\n';
    
    tasks.forEach(task => {
        // BUG: no escaping of commas or quotes in fields (CSV injection)
        csv += `${task.id},${task.title},${task.description},${task.priority},${task.status}\n`;
    });
    
    res.setHeader('Content-Type', 'text/csv');
    res.send(csv);
});

// Middleware error handler
router.use((err, req, res) => {  // BUG: missing 'next' parameter - Express won't recognize as error handler
    console.log(err);  // BUG: should use console.error
    res.status(500).json({ error: 'Internal server error' });
    // BUG: leaking no error details for debugging but also no structured logging
});

module.exports = router;
