clear;
data = load('20191210.txt');
%data = load('mtqData.txt');


B0 = data(1, 3);

V = data(2:end, 1);
I = data(2:end, 2);
B = data(2:end, 3);


B = B - B0;

minV = min(V);
maxV = max(V);
stepV = V(2) - V(1);
N = (maxV - minV)/stepV;

det_rec = zeros(N+1, 2);

for i = 0:N
    vi = minV + i*stepV;
    idx = (V > (vi - stepV/2) & V < (vi + stepV/2));
    Bi_rec = B(idx);
    a = max(Bi_rec);
    b = min(Bi_rec);
    
    det_rec(i+1, :) = [vi, a-b];
end
figure(2);
plot(det_rec(:, 1), det_rec(:, 2));
grid on;

detMax = max(det_rec(:,2));
BMax = max(B);
E = detMax/BMax*100


