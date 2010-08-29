//
//     Copyright (C) 2008 Loic Dachary <loic@dachary.org>
//
//     This program is free software: you can redistribute it and/or modify
//     it under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//
//     This program is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU General Public License for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
function CancelledError()
{
    this.reason = "Cancelled";
}

function Failure(err)
{
    this.err = err;
}

function Deferred()
{
    this.callbacks = [];
    this.fired = false;
    this.paused = 0;
    this.result = undefined;
    this.cancelled = false;
    
    this.call = function(value)
    {
        if(this.fired || value instanceof Deferred)
            return;
            
        this.fired = true;
        this.run(value);
    };

    this.cancel = function()
    {
        this.cancelled = true;
    }
    
    this.pause = function()
    {
        this.paused++;
    };
    
    this.unpause = function()
    {
        this.paused--;
        if(this.paused != 0)
            return;
        if(this.fired)
            this.run(this.result);
    };
    
    this.restart = function(value)
    {
        this.result = value;
        this.unpause();
    };
    
    this.addCallback = function(callback)
    {
        return this.addCallbacks(
        {
            onSuccess: callback,
            onFailure: function(err)
            {
                return err;
            }
        });
    };
    
    this.addErrback = function(callback)
    {
        return this.addCallbacks(
        {
            onFailure: callback,
            onSuccess: function(res)
            {
                return res;
            }
        });
    };
    
    this.addBoth = function(callback)
    {
        return this.addCallbacks(
        {
            onFailure: callback,
            onSuccess: callback
        });
    }
    
    this.addCallbacks = function(callback)
    {
        if(!callback)
            return this;
        this.callbacks.push(callback);
        
        if(!this.fired)
            return this;
        this.run(this.result);
        return this;
    };
    
    var deferred = this;
    this.run = function(value)
    {
        this.result = value;
        if(!this.paused)
        {
            while(this.callbacks.length > 0)
            {
                if(this.cancelled)
                {
                    this.result = new Failure(new CancelledError());
                    this.cancelled = false;
                }

                var callback = this.callbacks.shift();
                try
                {
                    this.result = this.result instanceof Failure
                        ? callback.onFailure(this.result)
                        : callback.onSuccess(this.result);
                }
                catch(e)
                {
                    this.result = new Failure(e);
                }
                
                if(this.result instanceof Deferred)
                {
                    this.pause();
                    this.result.addCallbacks(
                    {
                        onSuccess: function(res)
                        {
                            deferred.restart(res);
                            return null;
                        },
                        onFailure: function(err)
                        {
                            deferred.restart(err);
                            return null;
                        }
                    });
                    break;
                }
            }
        }
    };
}

Deferred.failure = function(err)
{
    if(!(err instanceof Failure))
        err = new Failure(err);
    var d = new Deferred();
    d.call(err);
    return d;
}

Deferred.success = function(value)
{
    var d = new Deferred();
    d.call(value);
    return d;
}
