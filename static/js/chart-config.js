document.addEventListener('DOMContentLoaded', function() {
    // Initialize specialty statistics chart if container exists
    const specialtyChartContainer = document.getElementById('specialty-chart');
    if (specialtyChartContainer) {
        // Get data from the data attributes
        const specialties = JSON.parse(specialtyChartContainer.dataset.specialties || '[]');
        const counts = JSON.parse(specialtyChartContainer.dataset.counts || '[]');
        
        const ctx = specialtyChartContainer.getContext('2d');
        
        // Define colors for each specialty
        const backgroundColors = [
            'rgba(75, 192, 192, 0.6)',
            'rgba(54, 162, 235, 0.6)',
            'rgba(255, 206, 86, 0.6)',
            'rgba(255, 99, 132, 0.6)',
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(199, 199, 199, 0.6)',
            'rgba(83, 102, 255, 0.6)',
            'rgba(40, 159, 64, 0.6)',
            'rgba(210, 99, 132, 0.6)',
            'rgba(120, 192, 192, 0.6)',
            'rgba(250, 162, 235, 0.6)',
            'rgba(190, 206, 86, 0.6)',
            'rgba(100, 99, 132, 0.6)',
            'rgba(180, 102, 255, 0.6)'
        ];
        
        // Create the chart
        const specialtyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: specialties,
                datasets: [{
                    label: 'Number of Patients',
                    data: counts,
                    backgroundColor: backgroundColors.slice(0, specialties.length),
                    borderColor: backgroundColors.map(color => color.replace('0.6', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Patient Distribution by Medical Specialty',
                        color: '#ffffff',
                        font: {
                            size: 18
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#ffffff',
                            precision: 0
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#ffffff'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    // Initialize appointment status chart if container exists
    const appointmentChartContainer = document.getElementById('appointment-chart');
    if (appointmentChartContainer) {
        // Get data from the data attributes
        const statuses = ['Scheduled', 'Completed', 'Cancelled'];
        const counts = [
            parseInt(appointmentChartContainer.dataset.scheduled || 0),
            parseInt(appointmentChartContainer.dataset.completed || 0),
            parseInt(appointmentChartContainer.dataset.cancelled || 0)
        ];
        
        const ctx = appointmentChartContainer.getContext('2d');
        
        // Create the chart
        const appointmentChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: statuses,
                datasets: [{
                    data: counts,
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(255, 99, 132, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Appointment Status Distribution',
                        color: '#ffffff',
                        font: {
                            size: 18
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff'
                    }
                }
            }
        });
    }
});
