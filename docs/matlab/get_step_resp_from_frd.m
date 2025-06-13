function step_resp = get_step_resp_from_frd(G, f_max)

    % Extract complex frequency response
    g = squeeze(G.ResponseData);
    if isnan(abs(g(1))) || isinf(abs(g(1)))
        g(1) = abs(g(2));
    end

    % Set frequencies above f_max_hz to zero
    g(G.Frequency > f_max) = 0;

    % Construct full spectrum
    g = [g; conj(g(end-1:-1:2))];

    % Step response is cumulative sum of real part of IFFT
    step_resp = cumsum(real(ifft(g)));

end