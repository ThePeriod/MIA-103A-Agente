// static/script.js

document.getElementById('simulation-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const num_intersections = document.getElementById('num_intersections').value;
    const timeout = document.getElementById('timeout').value;
    const strategy = document.getElementById('strategy').value;
    const levy_scale = document.getElementById('levy_scale').value;
    const max_wait_time = document.getElementById('max_wait_time').value;

    const data = {
        num_intersections: num_intersections,
        timeout: timeout,
        strategy: strategy,
        levy_scale: levy_scale,
        max_wait_time: max_wait_time
    };

    fetch('/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            document.getElementById('results').style.display = 'block';
            renderChart(result);
        } else {
            alert(result.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function renderChart(result) {
    const ctx = document.getElementById('waitTimesChart').getContext('2d');

    const labels = result.num_vehicles.map((_, index) => `Intersección ${index + 1}`);

    const data = {
        labels: labels,
        datasets: [
            {
                label: 'Tiempo de Espera (s)',
                data: result.wait_times,
                backgroundColor: 'rgba(54, 162, 235, 0.6)'
            },
            {
                label: 'Duración Luz Verde (s)',
                data: result.green_light_times,
                backgroundColor: 'rgba(75, 192, 192, 0.6)'
            },
            {
                label: 'Número de Vehículos',
                data: result.num_vehicles,
                backgroundColor: 'rgba(255, 99, 132, 0.6)'
            }
        ]
    };

    const options = {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };

    if (window.waitTimesChart instanceof Chart) {
        window.waitTimesChart.destroy();
    }

    window.waitTimesChart = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: options
    });
}
