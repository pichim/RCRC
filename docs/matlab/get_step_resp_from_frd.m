function step_resp = get_step_resp_from_frd(G, f_max)

    % Extract complex frequency response
    g = squeeze(G.ResponseData);
    if isnan(abs(g(1))) % TODO: interpolate based on point 2 and 3
        g(1) = g(2);
    end

    % Get frequency vector
    freq = G.Frequency;

    % Set frequencies above f_max_hz to zero
    g(freq >= f_max & freq <= freq(end) - f_max + freq(2)) = 0;

    % Step response is cumulative sum of real part of IFFT
    step_resp = cumsum(real(ifft(g)));

end