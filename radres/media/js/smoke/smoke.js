var smoketimeout;
var smoke = {

	pageload: function(){
    if (window.addEventListener) {
        window.addEventListener('load', function(){
    	    smoke.bodyload();
        }, false);
    } else if (window.attachEvent) {
        window.attachEvent('onload', function(){
    	    smoke.bodyload();
        });
    }
	},

	bodyload: function(){
		if (!document.getElementById('smoke-out')){
			var ff = document.createElement('div');
					ff.setAttribute('id','smoke-out');
					ff.setAttribute('class','smoke-base');
					document.body.appendChild(ff);
		}
	},
	
	forceload: function(){
  	smoke.bodyload();
	},

	build: function(e,f){
		e = e.replace(/\n/g,'<br />');
		e = e.replace(/\r/g,'<br />');
		var prompt = '';
		if (f.type == 'prompt'){
			prompt = 
				'<div class="dialog-prompt">'+
						'<input id="dialog-input" type="text" />'+
					'</div>';
		}
		
		var buttons = '';
		if (f.type != 'signal'){
			buttons = '<div class="dialog-buttons">';
			if (f.type == 'alert'){
				buttons +=
					'<button id="alert-ok">OK</button>';
			}
			
			if (f.type == 'prompt' || f.type == 'confirm'){
				buttons +=
					'<button id="'+f.type+'-cancel" class="cancel">Cancel</button>'+
					'<button id="'+f.type+'-ok">OK</button>';
			}
			
			buttons += '</div>';
		}

		var box = 
		'<div id="smoke-bg"></div>'+
		'<div class="dialog smoke">'+
			'<div class="dialog-inner">'+
					e+
					prompt+
					buttons+			
			'</div>'+
		'</div>';

		var ff = document.getElementById('smoke-out');
				ff.innerHTML = box;
				ff.className = 'smoke-base smoke-visible';

		// clear the timeout if it's already been activated
		if (smoketimeout){
				clearTimeout(smoketimeout);
		}
		
		// close on background click
		var g = document.getElementById('smoke-bg');
				if (g.addEventListener) {
				    g.addEventListener("click",function(){
				    	smoke.destroy(f.type);
				    	if (f.type == 'prompt' || f.type == 'confirm'){
				    		f.callback(false);
				    	}
				    }, false);
                } else {
				    g.attachEvent("onclick",function(){
				    	smoke.destroy(f.type);
				    	if (f.type == 'prompt' || f.type == 'confirm'){
				    		f.callback(false);
				    	}
				    });
                }




		// listeners for button actions

		if (f.type == 'alert'){
			// return true
			var h = document.getElementById('alert-ok');
					if (h.addEventListener) {
					    h.addEventListener("click",function(){
					    	smoke.destroy(f.type);
					    }, false);
                    } else {
					    h.attachEvent("onclick",function(){
					    	smoke.destroy(f.type);
					    });
                    }

			// listen for enter key or space, close it
			document.onkeyup = function(e){
				if (e.keyCode == 13 || e.keyCode == 32){
					smoke.destroy(f.type);
				}
			};
		}
		
		if (f.type == 'confirm'){
			// return false
			var h = document.getElementById('confirm-cancel');
					if (h.addEventListener) {
					    h.addEventListener("click",function(){
					    			smoke.destroy(f.type);
					    			f.callback(false);
					    }, false);
                    } else {
					    h.attachEvent("onclick",function(){
					    			smoke.destroy(f.type);
					    			f.callback(false);
					    });
                    }
			
			
			// return true
			var i = document.getElementById('confirm-ok');
					if (i.addEventListener) {
					    i.addEventListener("click",function(){
					    			smoke.destroy(f.type);
					    			f.callback(true);
					    }, false);
                    } else {
					    i.attachEvent("onclick",function(){
					    			smoke.destroy(f.type);
					    			f.callback(true);
					    });
                    }
					
			// listen for enter key or space, close it & return true
			document.onkeyup = function(e){
				if (e.keyCode == 13 || e.keyCode == 32){
					smoke.destroy(f.type);
					f.callback(true);
				}
			};

		}
		
		if (f.type == 'prompt'){
			// focus on input
			var pi = document.getElementById('dialog-input');
				
				setTimeout(function(){
					pi.focus();
					pi.select();
				},100);

			// return false
			var h = document.getElementById('prompt-cancel');
					if (h.addEventListener) {
					    h.addEventListener("click",function(){
					    			smoke.destroy(f.type);
					    			f.callback(false);
					    }, false);
                    } else {
					    h.attachEvent("onclick",function(){
					    			smoke.destroy(f.type);
					    			f.callback(false);
					    });
                    }

			// return	contents of input box
			var j = document.getElementById('dialog-input');
			var i = document.getElementById('prompt-ok');
					if (i.addEventListener) {
					    i.addEventListener("click",function(){
					    			smoke.destroy(f.type);
					    			f.callback(j.value);
					    }, false);
                    } else {
					    i.attachEvent("onclick",function(){
					    			smoke.destroy(f.type);
					    			f.callback(j.value);
					    });
                    }
					
			// listen for enter
			document.onkeyup = function(e){
				if (e.keyCode == 13){
					smoke.destroy(f.type);
					f.callback(j.value);
				}
			};
		}



		// close after f.timeout ms
		if (f.type == 'signal'){
			smoketimeout = setTimeout(function(){
				smoke.destroy(f.type);
			},f.timeout);
		}
		
	},
	
	destroy: function(type){				
		var box = document.getElementById('smoke-out');
				box.setAttribute('class','smoke-base');

			
			// confirm/alert/prompt remove click listener
			if (g = document.getElementById(type+'-ok')){
				if (g.removeEventListener) {
                    g.removeEventListener("click", function(){}, false);
                } else {
                    g.detachEvent("onclick", function(){});
                }
				
				// remove keyup listener
				document.onkeyup = null;
			}
			
			// confirm/prompt remove click listener
			if (h = document.getElementById(type+'-cancel')){

				if (h.removeEventListener) {
                    h.removeEventListener("click", function(){}, false);
                } else {
                    h.detachEvent("onclick", function(){});
                }
			}
	},

	alert: function(e){
		smoke.build(e,{type:'alert'});
	},
	
	signal: function(e,f){
		if (typeof(f) == 'undefined'){
			f = 5000;
		}
		smoke.build(e,{type:'signal',timeout:f});
	},
	
	confirm: function(e,f){
		smoke.build(e,{type:'confirm',callback:f});
		
	},
	
	prompt: function(e,f){
		return smoke.build(e,{type:'prompt',callback:f});
	}
	
};

// and start this
smoke.pageload();




// future

	// maybe ie (8-) support (event handlers, cat monocles)

	// custom prefs
		// custom true/false button text options

