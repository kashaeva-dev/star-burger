var rows = document.querySelectorAll('tr'); // Получаем все строки таблицы

for (var i = 1; i < rows.length; i++) {
  var row = rows[i];
  var cell = row.querySelector('td:nth-child(9)'); // Выбираем ячейку с Ресторанами

  var a = cell.getElementsByTagName('summary')[0];

  a.addEventListener('click', function () {
    if (!this.clicked) {
      this.clicked = true;
      this.innerHTML = '<i class="fa fa-caret-down fa-lg"></i> Скрыть';
    } else {
      this.clicked = false;
      this.innerHTML = '<i class="fa fa-caret-right fa-lg"></i> Показать';
    }
  }, false);
}
