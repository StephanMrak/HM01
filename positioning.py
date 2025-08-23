import numpy as np
import os
from scipy.signal import find_peaks
import scipy
import itertools
#from numba import njit

s = 0
c = 1595  # Speed of sound in the sheet (m/s)
z__1 = 0.0
z__2 = z__1
z__3 = 0.0  
z__4 = z__3

#@njit
def getTimeDifferences(x,y, widthD, heightD):
    zUpper = -0.0
    zLower = -0.0
    s = (zLower - zUpper) / heightD
    z = y * s + zUpper
    l1 = np.sqrt(x**2 + y**2 + z**2)
    l2 = np.sqrt((widthD - x)**2 + y**2 + z**2)
    l3 = np.sqrt((widthD - x)**2 + (heightD - y)**2 + z**2)
    l4 = np.sqrt(x**2 + (heightD - y)**2 + z**2)

    t12 = (l2-l1)/c
    t13 = (l3-l1)/c
    t14 = (l4-l1)/c
    t23 = (l3-l2)/c
    t24 = (l4-l2)/c
    t34 = (l4-l3)/c

    return [t12,t13,t14,t23,t24,t34]

#@njit
def getJacobian2d(x, y, y__1, y__2, y__3, y__4, widthD):
    x__2 = widthD
    x__3 = widthD
    t43 = y * s + z__1;
    t44 = y - y__4;
    t42 = t43 * t43;
    t55 = x * x + t42;
    t36 = np.power(t44 * t44 + t55, -.5);
    t60 = t36 * x;
    t45 = y - y__3;
    t48 = x - x__3;
    t33 = np.power(t45 * t45 + t48 * t48 + t42, -.5);
    t54 = t43 * s + y;
    t59 = t33 * (-y__3 + t54);
    t58 = t33 * t48;
    t46 = y - y__2;
    t49 = x - x__2;
    t34 = np.power(t46 * t46 + t49 * t49 + t42, -.5);
    t57 = t34 * t49;
    t56 = t36 * (-y__4 + t54);
    t47 = y - y__1;
    t37 = np.power(t47 * t47 + t55, -.5);
    t32 = t37 * (-y__1 + t54);
    t35 = t37 * x;
    t31 = t34 * (-y__2 + t54);
    return np.array([[t35 - t57,t32 - t31],[t35 - t58, t32 - t59],[t35 - t60, t32 - t56],[t57 - t58, t31 - t59],[t57 - t60, t31 - t56],[t58 - t60, -t56 + t59]])

#@njit
def getResidual2d(x,y,t,y__1,y__2,y__3,y__4, widthD):
    x__2 = widthD
    x__3 = widthD
    t__12, t__13, t__14, t__23, t__24,t__34 = t
    t80 = y * s + z__1;
    t79 = t80 * t80;
    t88 = x * x + t79;
    t86 = x - x__2;
    t85 = x - x__3;
    t84 = y - y__1;
    t83 = y - y__2;
    t82 = y - y__3;
    t81 = y - y__4;
    t78 = np.sqrt(t84 * t84 + t88);
    t77 = np.sqrt(t81 * t81 + t88);
    t76 = np.sqrt(t83 * t83 + t86 * t86 + t79);
    t75 = np.sqrt(t82 * t82 + t85 * t85 + t79);
    return np.array([[c * t__12 - t76 + t78],[c * t__13 - t75 + t78],[c * t__14 - t77 + t78],[c * t__23 - t75 + t76],[c * t__24 + t76 - t77],[c * t__34 + t75 - t77]])


#Find positive peaks in the area of the onset
#@njit 
def extract_indices(peakIdx, onset, peaksBefore = 1, peaksAfter = 1, max_distance = 50):
    # Find the next index in peakIdx that is greater than or equal to onset
    closest_index = None
    for idx in peakIdx:
        if idx >= onset:
            closest_index = idx
            break  # Stop at the first match
    #closest_index = next((idx for idx in peakIdx if idx >= onset), None)
    if closest_index is None:
        return np.empty(0, dtype=np.int64)

    # Find the position of the closest index in the peakIdx list
    pos = -1
    for i in range(len(peakIdx)):
        if peakIdx[i] == closest_index:
            pos = i
            break  # Stop once found
    #pos = peakIdx.tolist().index(closest_index)
    
    # Extract indices around the given index
    start = max(0, pos - peaksBefore)

    # Adjust the start index if the distance from onset to start exceeds max_distance
    while start < pos and (onset - peakIdx[start]) > max_distance:
        start += 1  # Move the start index forward to reduce the distance

    end = min(len(peakIdx), pos + peaksAfter)
    
    return peakIdx[start:end]

#@njit
def update_variance(state, x):
    """ Update the variance state with a new data point. """
    n, mean, m2 = state
    n += 1
    delta = x - mean
    mean += delta / n
    delta2 = x - mean
    m2 += delta * delta2
    return (n, mean, m2)

#@njit
def remove_variance(state, x):
    """ Remove a data point from the variance state. """
    n, mean, m2 = state
    if n <= 1:
        return (0, 0.0, 0.0)
    n -= 1
    delta = x - mean
    mean -= delta / n
    m2 -= delta * (x - mean)
    return (n, mean, m2)

#@njit
def compute_variance(state):
    """ Compute variance from state. """
    n, mean, m2 = state
    return m2 / (n - 1) if n > 1 else 0.0

#@njit
def var_state_from_numpy(data):
    """ Initialize an OnlineVariance state from NumPy array. """
    n = len(data)
    mean = np.mean(data)
    m2 = np.sum((data - mean) ** 2)
    return (n, mean, m2)


#@njit 
def compute_aic_optimized(data, offset, epsilon=1e-10):    
    # Left-side variance initialization using NumPy
    left_var_state = var_state_from_numpy(data[1:offset-1])

    # Right-side variance initialization using NumPy
    sampleLength = len(data)
    right_var_state = var_state_from_numpy(data[offset : sampleLength - offset - 1])

    # Compute AIC for each i using recursive variance
    aic = np.empty(sampleLength - 2 * offset - 1)
    outIdx = 0
    for i in range(offset + 1, sampleLength - offset - 1):

        left_var_state = update_variance(left_var_state, data[i-1])  # Expand left-side
        right_var_state = remove_variance(right_var_state, data[i])   # Shrink right-side

        var_left = compute_variance(left_var_state) + epsilon
        var_right = compute_variance(right_var_state) + epsilon

        aic[outIdx] = (i * np.log(var_left) + (sampleLength - i) * np.log(var_right))
        outIdx += 1

    return aic

#@njit 
def getMinAic(data, offset, end, epsilon=1e-10):    
    # Left-side variance initialization using NumPy
    left_var_state = var_state_from_numpy(data[1:offset-1])

    # Right-side variance initialization using NumPy
    sampleLength = len(data)
    right_var_state = var_state_from_numpy(data[offset : sampleLength - 1])

    # Compute AIC for each i using recursive variance
    minValue = 1e6
    minIndex = offset
    i = offset + 1
    while i < end:
        left_var_state = update_variance(left_var_state, data[i-1])  # Expand left-side
        right_var_state = update_variance(right_var_state, data[i])   # Shrink right-side

        var_left = compute_variance(left_var_state) + epsilon
        var_right = compute_variance(right_var_state) + epsilon

        aicVal = i * np.log(var_left) + (sampleLength - i) * np.log(var_right)
        if(aicVal < minValue):
            minValue = aicVal
            minIndex = i
        i += 1

    return minIndex

#@njit 
def runOptimization(lagsForSequence, heightD, widthD, u1, u2, u3, u4):
    # Calculate the position estimate
    posEstimate = np.array([[widthD/2],[heightD/2]])
    minNormRes = 1e6
    res =  np.ascontiguousarray(np.empty((0, 0), dtype=np.float64))
    isValid = False
    validPosition = np.array([[100],[100]], dtype=np.float64)
    for i in range(len(lagsForSequence)):
    #for lag in lagsForSequence:
        lag = lagsForSequence[i]
        posEstimate = np.array([[widthD/2],[heightD/2]])
        maxIter = 50
        y__1 = 0.0
        y__2 = 0.0
        y__3 = heightD
        y__4 = heightD
        for i in range(1,maxIter):
            J = getJacobian2d(posEstimate[0][0],posEstimate[1][0],y__1,y__2,y__3,y__4,widthD)
            res = getResidual2d(posEstimate[0][0],posEstimate[1][0],lag,y__1,y__2,y__3,y__4,widthD)
            #print(f"Residual: {res}")
            deltaPosition = np.linalg.inv((J.T @ J)) @ J.T @ res
            positionChangeLength = np.linalg.norm(deltaPosition) 
            if(positionChangeLength > 0.02):
                deltaPosition = 0.02/positionChangeLength*deltaPosition
            posEstimate = posEstimate - deltaPosition
            
            if(np.linalg.norm(deltaPosition) < 1e-4):
                break

            if (posEstimate[0][0] < 0) or (posEstimate[0][0] > widthD) or (posEstimate[1][0] < 0) or (posEstimate[1][0] > heightD):
                break
            resPos = 0.005
            x_index = int(posEstimate[0][0] / resPos) + 1
            y_index = int(posEstimate[1][0] / resPos) + 1
            fak =  1.0
            y__1 = u1[y_index, x_index]*fak
            y__2 = u2[y_index, x_index]*fak
            y__3 = heightD - u3[y_index, x_index]*fak
            y__4 = heightD - u4[y_index, x_index]*fak

        isInWindow = (posEstimate[0][0] > 0) and (posEstimate[0][0] < widthD) and (posEstimate[1][0] > 0) and (posEstimate[1][0] < heightD)
        if(isInWindow):
            normResVec = np.linalg.norm(res)
            if (minNormRes > normResVec):
                isValid = True
                minNormRes = normResVec
                #print(f"Position estimate: {posEstimate}")
                validPosition = posEstimate
    
    return (isValid, validPosition, minNormRes)


class PositionEstimator:
    def __init__(self, width = 0.370, height = 0.215, mode = 0):
        self.widthD = width
        self.heightD = height
        self.mode = mode
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'u_map.npy')
        self.u1 = np.load(file_path)  # Load the precomputed heatmap values
        self.u2 = np.fliplr(self.u1)        # Flip left-right
        self.u3 = np.flipud(self.u2)        # Then flip up-down
        self.u4 = np.flipud(self.u1)        # Just flip up-down


#import numpy as np
#import matplotlib.pyplot as plt
#from scipy.optimize import fsolve
#
## === Parameters ===
#a = 0.017       # distance from boundary to receiver (in c2 region)
#c1 = c     # speed of sound in sheet
#c2 = 330.0      # speed of sound in surroundings
#tMax = 1/454000    # given time difference
#xMax = .5
#yMax = .3
#resPos = 0.005     # resolution (number of points in each axis)
#resX = int(xMax/resPos) + 1
#resY = int(yMax/resPos) + 1
## === Ranges ===
#x_range = np.linspace(0, xMax, resX)
#y_range = np.linspace(yMax,0, resY)
#
# === Heatmap values ===
#u_map = np.full((resY, resX), np.nan)
#
## === Equation to solve for each (x, y) ===
#def solve_u(x, y):
#    def func(u):
#        T_RM1 = np.sqrt(x**2 + y**2) / c1 + a / c2
#        T_UM1 = np.sqrt(x**2 + (y - u)**2) / c1 + np.sqrt(a**2 + u**2) / c2
#        return T_RM1 - T_UM1 - tMax
#
#    # Initial guess for u
#    u0 = 0
#
#    try:
#        sol = fsolve(func, u0)
#        u_val = sol[0]
#        if 0 <= u_val <= y:  # Physically valid
#            return u_val
#    except Exception:
#        pass
#
#    return np.nan
# 
#
## === Compute heatmap ===
#for i, x in enumerate(x_range):
#    for j, y in enumerate(y_range):
#        u_map[j, i] = solve_u(x, y)
#np.save('u_map.npy', u_map)  # Save the computed heatmap values

    def estimatePosition(self, data):
        ch1, ch2, ch3, ch4, frequency = data 
        peakVectors = []
        deltaTime = 1/frequency
        if(self.mode == 0):
            sos = scipy.signal.butter(8, 45000, 'low', fs=frequency, output='sos')
            # Filter
            dataFiltered = (scipy.signal.sosfilt(sos, ch1),scipy.signal.sosfilt(sos, ch2),scipy.signal.sosfilt(sos, ch3),scipy.signal.sosfilt(sos, ch4))

            offset = 20
            sampleLength = len(ch1)
            searchWindow = int((1.5 * max(self.widthD, self.heightD))/(deltaTime * c))
            onsetIdx1 = getMinAic(dataFiltered[0], offset, sampleLength - offset - 1)
            offsetForFollowing=  onsetIdx1 - searchWindow
            endForFollowing = onsetIdx1 + searchWindow
            if(endForFollowing > sampleLength or offsetForFollowing < 0):
                print("Data not considered due to onset position!")
                return (False, [100,100], 1e6)

            onsetIdx2 = getMinAic(dataFiltered[1], offsetForFollowing, endForFollowing)
            onsetIdx3 = getMinAic(dataFiltered[2], offsetForFollowing, endForFollowing)
            onsetIdx4 = getMinAic(dataFiltered[3], offsetForFollowing, endForFollowing)
            onsetV = [onsetIdx1, onsetIdx2, onsetIdx3, onsetIdx4]

            # Stop here for too big diffs in onsets
            maxOnsettDiff = max(abs(x-y) for x,y in  itertools.combinations(onsetV,2))
            if(maxOnsettDiff >= searchWindow):
                print("Data not considered due to onset differences!")
                print(f"Max onset difference: {maxOnsettDiff}")
                return (False, [100,100], 1e6)
            
            # Detect peaks in the area of the onset
            peaksBefore = 1
            peaksAfter = 1
            for idx, onset in enumerate(onsetV):
                peakIdx, _ = find_peaks(dataFiltered[idx], distance=1, height=0.1, width=1)
                if len(peakIdx) == 0:
                    break
                indices = extract_indices(peakIdx, onset, peaksBefore, peaksAfter)
                if len(indices) == 0:
                    break
                peakVectors.append(indices)

            if len(peakVectors) < 4:
                #print("Data not considered due to missing peaks!")
                return (False, [100,100], 1e6) 

        elif self.mode == 1:
            peakFound = True
            for diffCh in (np.diff(ch1), np.diff(ch2), np.diff(ch3), np.diff(ch4)):
                # Find peaks in the channel
                index, _ = find_peaks(diffCh, distance=4, height=0.5, width=1)
                if len(index) == 0:
                    peakFound = False
                    break
                peakVectors.append([index[0]])
                
            if not peakFound:
                return (False, [100,100], 1e6)

        # Get all possible combinations of peaks and calculate the time difference between them
        lagsForSequence = []
        combinations = list(itertools.product(*peakVectors))
        for combination in combinations:
            peakIndices = list(combination)
            if peakIndices:
                # channel order for 0 and 1 is reverserd in the adc conversion (it's 1 0 2 3)
                lagAic12 = (peakIndices[1] - peakIndices[0] + 0.25)*deltaTime # + beacause channel 1 is sampled before 0
                lagAic13 = (peakIndices[2] - peakIndices[0] - 0.25)*deltaTime
                lagAic14 = (peakIndices[3] - peakIndices[0] - 0.5)*deltaTime
                lagAic23 = (peakIndices[2] - peakIndices[1] - 0.5)*deltaTime
                lagAic24 = (peakIndices[3] - peakIndices[1] - 0.75)*deltaTime
                lagAic34 = (peakIndices[3] - peakIndices[2] - 0.25)*deltaTime
                lagsForSequence.append(np.array([lagAic12, lagAic13, lagAic14, lagAic23, lagAic24, lagAic34],dtype=np.float64))  
                
        # Calculate the position estimate
        return runOptimization(np.array(lagsForSequence,dtype=np.float64), self.heightD, self.widthD, self.u1, self.u2, self.u3, self.u4)


