try {
    if (localStorage.getItem("IndexPopUp") === null) {
        $(document).ready(function () {
            $("#myModal").modal('show');
            localStorage.setItem('IndexPopUp', 'True');
            console.log(localStorage.getItem("IndexPopUp"));
        });
    }
  }
  catch(err) {
    console.log(err);
  }



$("#btnModeClose").on("click", function (e) {
    e.preventDefault();
    $("#myModal").modal("hide");
    $('#myModal').data("modal", null);
});