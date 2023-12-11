//never used this file

const hourEle = document.getElementById('id_hour')

function init()
{
	
}

//loads the picker with whatever's in the input box
function getTimeFromText(timePickable)
{
	const pattern = /^(/d+):(/d+) (AM|PM)$/
	const [hour, minute, mer] = Array.from(timePickable.value.match(pattern)).splice(1);
	
	return {hour, minute, mer};
}

function getSelectsFromPicker(timePicker)
{
	const [hour, minute, mer] = timePicker.querySelectorAll(".time-picker_select");
	
	return {hour, minute, mer};
}

function getTimeStringFromPicker(timePicker)
{
	const selects = getSelectsFromPicker(timePicker);
	
	return '${selects.hour.value}:${selects.minute.value} ${selects.mer.value}';
}


init();