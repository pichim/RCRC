function [step_resp, time] = get_step_resp_from_frd(G_frd, Ts, f_max)

    % handle function call without f_max specified
    if (~exist('f_max', 'var') || isempty(f_max))
        f_max = max(G_frd.Frequency);
    end

    g = squeeze(G_frd.ResponseData);
    if isnan(abs(g(1))) % Todo: interpolate based on point 2 and 3
        g(1) = g(2);
    end
    
    g(G_frd.Frequency >= f_max) = 0;
    
    step_resp = cumsum(real(ifft( g, 'symmetric' )));
    % use double the samling time because of the 'symmetric' option
    time = (0:length(step_resp)-1).' * 2*Ts;
end