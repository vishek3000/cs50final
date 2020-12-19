colors = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'];

const pollData = [
    {
        option: "Spiderman",
        votes: 11,
        color: "rgb(255, 99, 132)"
    },

    {
        option: "Batman",
        votes: 8,
        color: "rgb(3, 123, 252)"
    },

    {
        option: "Superman",
        votes: 4,
        color: "rgb(255, 47, 0)"
    },

    {
        option: "Ironman",
        votes: 14,
        color: "rgb(252, 173, 3)"
    },

    {
        option: "The Hulk",
        votes: 11,
        color: "rgb(6, 173, 0)"
    },

        {
        option: "Black Panther",
        votes: 13,
        color: "rgb(64, 64, 64)"
    },

    {
        option: "Other",
        votes: 7,
        color: "rgb(132, 107, 255)"
    }];


function rbgToRgba(rgb, alpha = 1){
    return `rgba(${rgb.substring(rgb.indexOf('(')+1, rgb.length-1).split(',').join()}, ${alpha})`;
}

Chart.defaults.global.defaultFontFamily = '"Montserrat", sans-serif';


const ctx = document.getElementById('chart').getContext('2d');
const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: colors,
        datasets: [{
            label: '# of Votes',
            data: pollData.map(pollOption => pollOption.votes),
            backgroundColor: pollData.map(pollOption => rbgToRgba(pollOption.color,0.75)),
            borderWidth: 1
        }]
    },
    options: {
        /*scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        }, */
        title:{
            display: true,
            text: "Custom Chart Title",
            fontColor: "#333",
            fontSize: 20,
            padding: 20
        },

        legend:{
         display: true
        }
    }
});