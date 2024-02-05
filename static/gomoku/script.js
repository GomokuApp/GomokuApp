function refresh() {
    fetch("/gomoku/api/"+ gameId + "/refresh")
            .then(response => response.json())
            .then(refreshScreen);

    const board = $('.board');

    if (window.matchMedia("(orientation:landscape)").matches) {
        board.css({
            'width': '',
            'height': board.width() + 'px'
        });
    } else {
        board.css({
            'width': board.height() + 'px',
            'height': ''
        });
    }
}

function renderPiece(row, column, color) {
    document.getElementsByClassName("triggers")[0].children[0]
                .children[row]
                .children[column]

                .children[0].children[0].setAttribute("src", "/static/gomoku/pieces/" + color + ".png")
}

let isMyTurn = false;
let myColor = null;

function refreshScreen(data) {
    console.log(data)
    let board = data.current_board
    isMyTurn = data.is_your_turn
    myColor = data.your_color
    currentPlayers = data.current_players
    currentTurn = data.current_turn

    if (data.ended) {
        alert("Game ended, " + data.won_color + " won")
        refresh()
    }

    for (let row = 0; row < 15; row++) {
        for (let column = 0; column < 15; column++) {
            let color = board[row][column]
            if (color !== null) {
                renderPiece(row, column, color)
            } else {
                renderPiece(row, column, "none")
            }
        }
    }

    for (const [color, user] of Object.entries(currentPlayers)) {
        let display = document.getElementsByClassName("player-display-property-" + color)[0];
        if (user != null) {
            let inner = `
                <p>`+ user.displayed_name +`</p>
                <img src="/static/gomoku/pieces/` + color +`.png" alt="Piece">
                `
            if (display.innerHTML !== inner)
                display.innerHTML = inner

            let avatar = `
                <img src="` + user.profile_picture + `" alt="Player Avatar">
                `

            if (document.getElementsByClassName("avatar-" + color)[0].innerHTML !== avatar)
                document.getElementsByClassName("avatar-" + color)[0].innerHTML = avatar
        } else {
            let inner = `
                <a onclick="fetch('/gomoku/api/` + gameId + "/" + color + `/join')">
                    Join as ` + color + `
                </a>
            `

            if (display.innerHTML !== inner)
                display.innerHTML = inner

            let avatar = `
                <img src="/static/gomoku/avatar/default.png" alt="Player Avatar">
                `

            if (document.getElementsByClassName("avatar-" + color)[0].innerHTML !== avatar)
                document.getElementsByClassName("avatar-" + color)[0].innerHTML = avatar
        }

        if (currentTurn === color)
            display.style.backgroundColor = "rgb(215, 184, 71)"
        else
            display.style.backgroundColor = null
    }
}

setInterval(
    refresh,
    500
) // online check every second

function placePiece(row, column) {
    console.log("" + row + ", " + column)
    fetch("/gomoku/api/"+ gameId + "/place_piece/" + row + "/" + column)
    // if (isMyTurn) {
    //     renderPiece(row, column, myColor)
    // }
}