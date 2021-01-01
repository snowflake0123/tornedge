export const generateFormData = (...props: any[]) => {
	const formData = new FormData();
	let data;

	if (props.length === 1 && typeof(props[0]) === "object") {
		data = props[0];
	} else {
		data = props
	}

	if (data.length % 2 === 0) {
		for (let i=0; i < data.length; i+=2) {
			formData.append(data[i], data[i+1]);
			// console.log(`${data[i]}: ${data[i+1]}`);
		}
	}

	return formData;
}
