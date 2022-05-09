var f1InitComplete=false
var icons=['home','table_view','monitoring','analytics']
var iconsTitle={'home':'Home/GIS','table_view':'Table','monitoring':'Plots','analytics':'Analytics'}
var showHide={'home':['mapContainer'],'table_view':[],
'monitoring':['plotContainer','query','toggle_query'],'analytics':[]}
var toggleEl=createToggle('toggle_query','Show/Hide query options')
var sleep = (ms) => new Promise((r)=>setTimeout(r,ms))

function initResize(){
	if(!(f1InitComplete)){
		let f1=document.getElementById('f1')
		f1.childNodes[1].style.width='80vw'
		f1.childNodes[1].style.height='60vh'
		f1.style.display='flex'
		f1.style.justifyContent='center'
		f1InitComplete=true
		// placeholder
		for (let entry of document.getElementsByClassName('Select-placeholder')){entry.style.color='gray'}
	}
}

function createToggle(id,title){
	let el=document.createElement('input')
	el.id=id
	el.type='range'
	el.min=0; el.max=1; el.step=1;
	el.title=title
	el.style.maxWidth='50px'
	return el
}

document.body.onload=async ()=>{
	// init
	while (!(document.getElementById('f1'))){await sleep(100)}
	document.body.style.margin="0px 0px 0px 0px"
	for (let entry of icons){
		for (let item of showHide[entry]){
			try{document.getElementById(item).style.display='none'}
			catch(e){console.log(e)}
		}
	}
	document.getElementById('options').style.justifyContent='center'

	// add nav
	document.head.innerHTML+='\\n<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght@300" rel="stylesheet" />'

	for (let entry of icons){
		let thisEl=document.createElement('span')
		thisEl.id='s_'+entry
		thisEl.className='material-symbols-outlined'
		thisEl.innerText=entry
		thisEl.style.fontSize='30px'
		thisEl.style.fontWeight='600'
		thisEl.style.color='black'
		thisEl.title=iconsTitle[entry]
		document.getElementById('options').appendChild(thisEl)
		thisEl.addEventListener('click',(e)=>{
			for (let entry of icons){
				document.getElementById('s_'+entry).style.color='black'
				for (let item of showHide[entry]){document.getElementById(item).style.display='none'}
			}
			thisEl.style.color='white'
			for (let item of showHide[entry]){document.getElementById(item).style.display=''}
			if (entry=='monitoring'){initResize()}
		})
	}
	document.getElementById('s_home').style.color='white'
	document.getElementById('b1').innerText='Update'
	document.getElementById('mapContainer').style.display='flex'

	// toggle
	toggleEl.style.position='absolute'
	toggleEl.style.top=document.body.getClientRects()[0]['top']+10+'px'
	toggleEl.style.left=document.body.getClientRects()[0]['right']-100+'px'
	document.body.appendChild(toggleEl)

	toggleEl.addEventListener('change',(e)=>{
		if(toggleEl.value==1){document.getElementById('query').style.display=''}
		else{document.getElementById('query').style.display='none'}
	})

}

window.onresize=()=>{
	let f1=document.getElementById('f1')
	f1.childNodes[1].style.width='80vw'
	f1.childNodes[1].style.height='60vh'
	f1.style.display='flex'
	f1.style.justifyContent='center'

	// toggle
	toggleEl.style.top=document.body.getClientRects()[0]['top']+10+'px'
	toggleEl.style.left=document.body.getClientRects()[0]['right']-100+'px'
}