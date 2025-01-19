function renderChart(canvasId, labels, points, calories, title) {
    console.log("here");
    
    if(labels.length == 0) {
        labels = ['No Data'];
    }
    if(points.length == 0) {
        points = [0];
    }
    if(calories.length == 0) {
        calories = [0];
    }    

    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: points,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                fill: true,
                yAxisID: 'y'
            },
        {
            label: 'Calories',
            data: calories,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1,
            yAxisID: 'y1'
        }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Points'
                    },
                    ticks: {
                        beginAtZero: true
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Calories'
                    },
                    ticks: {
                        beginAtZero: true
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            }
        }
    });
}
