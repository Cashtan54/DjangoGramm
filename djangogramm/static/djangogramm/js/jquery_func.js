$(document).ready(function(){
        $("input[type='submit']").click(function(e){
            if (this.value == 'Create post') {
                var $fileUpload = $("input[type='file']");
                if (parseInt($fileUpload.get(0).files.length)>5){
                 alert("You can only upload a maximum of 5 files");
                 e.preventDefault();
                } else if (parseInt($fileUpload.get(0).files.length)==0){
                 alert("You have to upload at least 1 file");
                 e.preventDefault();
            };
        };
});
});